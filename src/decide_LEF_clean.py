import sys
import argparse

from pysat.solvers import Glucose4, Minisat22
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.examples.mcsls import MCSls
from pysat.formula import WCNF
from threading import Timer
import matplotlib.pyplot as plt
import random
import networkx as nx
import time

from collections import defaultdict




import graphviz
from utils import *


class LEF_Solver:
    def __init__(self, agents, objects, social, formulation="consequence", house_alloc="auto", timeout = 300):
        self.n = len(agents)
        self.agents = agents
        self.objects = objects 
        self.social = social
        self.alloc_vars = []
        self.timeout = timeout

        self.formulation = formulation
        self.house_alloc = house_alloc if house_alloc != "auto" else "both"
        if self.formulation not in ["pairs", "complement", "consequence", "special"]:
            print(f"\"{self.formulation}\": unknown formulation (\"pairs\", \"complement\",\"consequence\",\"special\")")
            exit(-1)
        if self.house_alloc not in ["agents", "objects", "both", 'partial']:
            print(f"\"{self.house_alloc}\": unknown house_alloc (\"agents\", \"objects\", \"both\", \"auto\")")
            exit(-1)
        n_vars = 0
        alloc_var_id = 0

        self.lit_meaning = dict()

        for agent in agents:
            self.alloc_vars.append([])
            for obj in objects:
                n_vars += 1
                alloc_var_id += 1
                self.alloc_vars[agents.index(agent)].append(alloc_var_id)
                self.lit_meaning[alloc_var_id] =  f"alloc({agent},{obj})"
                
        self.clause2meaning = dict()
        self.n_constraints = 0
        self.clauses = []
        self.soft_clauses_copy = []


    def add_house_allocation_structure_clauses(self):
        house_alloc_clauses = [None]*(self.n + self.n*self.n*(self.n-1)//2)*(2 if self.house_alloc == "both" else 1)
        house_alloc_clause_count = 0
        if self.house_alloc == "agents" or self.house_alloc == "both":
            for agent_id in range(self.n):
                at_least_one = []
                for obj_id in range(self.n):
                    at_least_one.append(self.alloc_vars[agent_id][obj_id])
                house_alloc_clauses[house_alloc_clause_count] = at_least_one
                #self.clauses.append(at_least_one)
                self.clause2meaning[tuple(at_least_one)] = f"at least one object for agent {agents[agent_id]}"
                house_alloc_clause_count += 1
                self.n_constraints += 1

            for obj_id in range(self.n):
                for agent_id in range(self.n):
                    for agent2_id in range(agent_id+1, self.n):
                        clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent2_id][obj_id]]
                        house_alloc_clauses[house_alloc_clause_count] = clause
                        #self.clauses.append(clause)
                        self.clause2meaning[tuple(clause)] = f"only one agent for object {objects[obj_id]} ({agents[agent_id]},{agents[agent2_id]})"
                        house_alloc_clause_count += 1
                        self.n_constraints += 1
        
        if self.house_alloc == "objects" or self.house_alloc == "both":
            for obj_id in range(self.n):
                at_least_one = []
                for agent_id in range(self.n):
                    at_least_one.append(self.alloc_vars[agent_id][obj_id])
                house_alloc_clauses[house_alloc_clause_count] = at_least_one
                #self.clauses.append(at_least_one)
                self.clause2meaning[tuple(at_least_one)] = f"at least one agent per object {objects[obj_id]}"
                house_alloc_clause_count += 1
                self.n_constraints += 1
            for agent_id in range(self.n):
                for obj_id in range(self.n):
                    for obj2_id in range(obj_id+1, self.n):
                        clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent_id][obj2_id]]
                        house_alloc_clauses[house_alloc_clause_count] = clause
                        #self.clauses.append(clause)
                        self.clause2meaning[tuple(clause)] = f"only one object per agent {agents[agent_id]} ({objects[obj_id]},{agents[obj2_id]})"
                        house_alloc_clause_count += 1
                        self.n_constraints += 1
        #print(house_alloc_clause_count, (self.n + self.n*self.n*(self.n-1)//2)*(2 if self.house_alloc == "both" else 1))
        self.clauses.extend(house_alloc_clauses)

    def add_LEF_clauses(self):
        ordObj_pref = [None]*self.n
        for agent_id in range(self.n):
            objId2prefLevel = [None]*self.n
            prefs_agent_i = preferences[agent_id]
            for i in range(self.n):
                objId2prefLevel[self.objects.index(prefs_agent_i[i])] = i
            ordObj_pref[agent_id] = objId2prefLevel
        
        if self.formulation == "pairs" or self.formulation == "special":
            for agent1_id, agent2_id in social:
                ordObj1 = ordObj_pref[agent1_id]
                ordObj2 = ordObj_pref[agent2_id]        
                for objAssignedTo2 in range(len(ordObj1)):
                    for objAssignedTo1 in range(len(ordObj2)):
                        # agent1 -> agent2 or agent2 -> agent1
                        if ordObj1[objAssignedTo1] > ordObj1[objAssignedTo2] or ordObj2[objAssignedTo2] > ordObj2[objAssignedTo1]:
                            clause = [-self.alloc_vars[agent1_id][objAssignedTo1], -self.alloc_vars[agent2_id][objAssignedTo2]]
                            self.clauses.append(clause)
                            self.clause2meaning[tuple(clause)] =f"not both alloc_({self.agents[agent1_id]},{self.objects[objAssignedTo1]}) and alloc_({self.agents[agent2_id]},{self.objects[objAssignedTo2]})"
                            self.n_constraints += 1

        if self.formulation == "complement":
            unknown_agents = [None]*self.n
            for agent1_id in range(self.n):
                unknown_agents[agent1_id] = list()
            for agent1_id in range(self.n):
                for agent2_id in range(self.n):
                    if (agent1_id != agent2_id) and not (((agent1_id,agent2_id) in self.social) or ((agent2_id,agent1_id) in self.social)):
                        unknown_agents[agent1_id].append(agent2_id)
            
            #for agent1_id in range(self.n):
            #    print(unknown_agents[agent1_id])
            for objAssignedTo1 in range(self.n):
                for objAssignedTo2 in range(self.n):
                    for agent1_id in range(self.n):
                        ordObj1 = ordObj_pref[agent1_id]
                        if ordObj1[objAssignedTo1] > ordObj1[objAssignedTo2]:
                            clause = [-self.alloc_vars[agent1_id][objAssignedTo1]]
                            for agent2_id in unknown_agents[agent1_id]:
                                #ordObj2 = ordObj_pref[agent2_id]
                                #if ordObj2[objAssignedTo2] > ordObj2[objAssignedTo1]:
                                clause.append(self.alloc_vars[agent2_id][objAssignedTo2])
                            
                            self.clauses.append(clause)
                            self.n_constraints += 1

        if self.formulation == "consequence" or self.formulation == "special":

            for agent1_id, agent2_id in self.social:
                ordObj1 = ordObj_pref[agent1_id]
                ordObj2 = ordObj_pref[agent2_id]
                for objAssignedTo2 in range(len(ordObj1)):
                    # agent1 -> agent2
                    clause = [-self.alloc_vars[agent2_id][objAssignedTo2]]
                    meaning = f"alloc({self.agents[agent2_id]},{self.objects[objAssignedTo2]}) ->"
                    obj_possible_to_assign = []
                    for objAssignedTo1 in range(len(ordObj2)):
                        if ordObj1[objAssignedTo1] < ordObj1[objAssignedTo2] and ordObj2[objAssignedTo1] > ordObj2[objAssignedTo2]:
                            clause.append(self.alloc_vars[agent1_id][objAssignedTo1])
                            obj_possible_to_assign.append(self.objects[objAssignedTo1])
                    self.clauses.append(clause)
                    if obj_possible_to_assign == []:
                        meaning += f" False (agent {self.agents[agent1_id]})"
                    else:
                        meaning += f" alloc({self.agents[agent1_id]},{{{'|'.join(obj_possible_to_assign)}}})"
                    self.clause2meaning[tuple(clause)] = meaning
                    self.n_constraints += 1
                for objAssignedTo1 in range(len(ordObj2)): 
                    # agent2 -> agent1
                    clause = [-self.alloc_vars[agent1_id][objAssignedTo1]]
                    meaning = f"alloc({self.agents[agent1_id]},{self.objects[objAssignedTo1]}) ->"
                    obj_possible_to_assign = []
                    for objAssignedTo2 in range(len(ordObj1)):
                        if ordObj2[objAssignedTo2] < ordObj2[objAssignedTo1] and ordObj1[objAssignedTo2] > ordObj1[objAssignedTo1]:
                            clause.append(self.alloc_vars[agent2_id][objAssignedTo2])
                            obj_possible_to_assign.append(self.objects[objAssignedTo2])
                    self.clauses.append(clause)
                    if obj_possible_to_assign == []:
                        meaning += f" False (agent {self.agents[agent2_id]})"
                    else:
                        meaning += f" alloc({self.agents[agent2_id]},{{{'|'.join(obj_possible_to_assign)}}})"
                    self.clause2meaning[tuple(clause)] = meaning
                    self.n_constraints += 1
            #print(lef_clause_count, 2*len(social)*self.n)

    def add_limited_house_alloc_clauses(self,agent_objects):
        agent = agent_objects[0]
        obj = agent_objects[1]
        at_least_one = []

        if agent == '*' and obj == '*':
            self.house_alloc = 'both'
            self.add_house_allocation_structure_clauses()
            return
        elif obj == '*':
            agent_id = self.agents.index(agent)
            for obj_id in range(self.n):
                at_least_one.append(self.alloc_vars[agent_id][obj_id])
        elif agent == '*':
            obj_id = self.objects.index(obj)
            for agent_id in range(self.n):
                at_least_one.append(self.alloc_vars[agent_id][obj_id])
        else:
            agent_id = self.agents.index(agent)
            for obj_ in agent_objects[1:]:
                obj_id = self.objects.index(obj_)
                at_least_one.append(self.alloc_vars[agent_id][obj_id])
        self.clauses.append(at_least_one)  
        self.n_constraints += 1


        # add every unicity clauses
        for obj_id in range(self.n):
            for agent_id in range(self.n):
                for agent2_id in range(agent_id+1, self.n):
                    clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent2_id][obj_id]]
                    self.clauses.append(clause)
                    self.clause2meaning[tuple(clause)] = f"only one agent for object {objects[obj_id]} ({agents[agent_id]},{agents[agent2_id]})"
                    self.n_constraints += 1
        for agent_id in range(self.n):
            for obj_id in range(self.n):
                for obj2_id in range(obj_id+1, self.n):
                    clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent_id][obj2_id]]
                    self.clauses.append(clause)
                    self.clause2meaning[tuple(clause)] = f"only one object per agent {agents[agent_id]} ({objects[obj_id]},{agents[obj2_id]})"
                    self.n_constraints += 1


    def solve(self):
        g = Minisat22(bootstrap_with=self.clauses, use_timer=True)
        
        def interrupt(s):
            s.interrupt()
        
        timer = Timer(self.timeout, interrupt, [g])
        timer.start()
        self.LEF = g.solve_limited(expect_interrupt=True)
        if self.LEF != None:
            self.solving_time = g.time()
            self.model = g.get_model()
        timer.cancel()
        g.delete()    

    def computeMUS(self, draw = False):
        wcnf = WCNF()
        wcnf.extend([[lit for lit in clause] for clause in self.clauses], weights=[1]*len(self.clauses))
        musx = MUSX(wcnf, verbosity=0)
        mus = musx.compute()
        if mus == None:
            print("Solution Found.")
            exit(0)
        else:
            clause_mus = []
            for i in range(len(mus)):
                clause_mus.append(self.clauses[mus[i]-1])
        ids, one, two, set_ag, set_obj  = decode_mus(clause_mus, self.agents, self.objects,self.alloc_vars )
        #print(one, two, set_ag, set_obj )
        print()
        if draw:
            draw_other_dag(clause_mus, "Full MUS DAG", self.lit_meaning, self.clause2meaning)

    def print_model(self):
        print(f"number of constraints: {self.n_constraints}")
        if self.LEF:
            print("LEF allocation found")
            parse_model(self.model, self.agents, self.objects, self.alloc_vars)
        else:
            print("No LEF allocation")

    def check(self):
        ordObj_pref = [None]*self.n
        for agent_id in range(self.n):
            objId2prefLevel = [None]*self.n
            prefs_agent_i = preferences[agent_id]
            for i in range(self.n):
                objId2prefLevel[self.objects.index(prefs_agent_i[i])] = i
            ordObj_pref[agent_id] = objId2prefLevel

        agent_id2obj_id = [] 
        for agent_id in range(len(agents)):
            for obj_id in range(len(objects)):
                if self.alloc_vars[agent_id][obj_id] in self.model:
                    agent_id2obj_id.append(obj_id)
        #check if LEF
        for agent1_id, agent2_id in self.social:
            ordObj1 = ordObj_pref[agent1_id]
            ordObj2 = ordObj_pref[agent2_id]
            assert(ordObj1[agent_id2obj_id[agent1_id]] < ordObj1[agent_id2obj_id[agent2_id]])
            assert(ordObj2[agent_id2obj_id[agent2_id]] < ordObj2[agent_id2obj_id[agent1_id]])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("pref_file", type=argparse.FileType('r'), help="path to the preference file")
    parser.add_argument("social_file", type=argparse.FileType('r'), help="path to the social file")
    lef = parser.add_argument_group("LEF clauses")
    lef.add_argument("--LEF", choices=["consequence", "complement", "pairs", "special"], default='consequence', help="precise the LEF clauses to use. 'both' uses both the consequence and pairs clauses")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-o", "--out", type=argparse.FileType('a'), help="optional file to print the output (append)")
    parser.add_argument("--mus", action="store_true", help="if set compute a mus instead of the allocation (only works if formula is unsat)")
    parser.add_argument("--draw", action="store_true", help="if set and --mus is set then output a graph of the MUS (old version, made with graphviz)")
    parser.add_argument("-t","--timeout", type=int, default=150, help="define the timeout of the _solving_ time. Default is 150 sec")


    ha = parser.add_argument_group("House alloc clauses")
    ha.add_argument("--partial", help="If chosen, the solver will not use all the unicity and allocation clauses. \
                        If followed by 'agents' or 'objects' alone, will use only the appropriate 'at least one' and 'not both' clauses.\
                        If followed by an agent and '*' pair (e.g. '1,*'), will create the at least one clause for this agent. Similar for '*' followed by an object (e.g. '*,o1')\
                        Otherwise, the arguments will be read as 'agent_name,obj1,obj2,...,objk', meaning that agent with agent_name\
                        will be allowed to get any object from of the limited set of objects")
    
    args = parser.parse_args()

    preferences = []

    preferences_lines = args.pref_file.read().splitlines()

    for pref_line in preferences_lines:
        preferences.append(parse_preference_line(pref_line))


    agents, social, number_of_edges = parse_tgf(args.social_file)

    objects = get_objects_from_preferences(preferences)

    if len(objects) != len(agents):
        sys.exit(f"The number of agents ({len(agents)}) must be the same as the number of objects ({len(objects)}).")

    if args.LEF:
        formulation = args.LEF
    else:
        formulation = "special"


    if args.partial:
        if len(args.partial.split(",")) > 1:
            house_alloc = 'partial'
        else:
            house_alloc = args.partial
    else:
        house_alloc = "both"
    start = time.time()

    solver = LEF_Solver(agents, objects, social, formulation=formulation, house_alloc=house_alloc, timeout = args.timeout)
    if house_alloc != "partial": 
        solver.add_house_allocation_structure_clauses()
    else:
        solver.add_limited_house_alloc_clauses(args.partial.split(","))
    solver.add_LEF_clauses()
    end_construction = time.time()
    
    if args.mus:
        solver.computeMUS(draw=args.draw)
        exit()
    solver.solve()
    if solver.LEF != None:
        solver.print_model()
        if solver.LEF:
            solver.check()
            print("check passed")

    if args.out:
        if solver.LEF != None:
            print(f"{end_construction - start + solver.solving_time} {end_construction - start} {solver.solving_time} {solver.LEF}", file=args.out)
        else:
            print(f"timeout! {solver.timeout}", file=args.out)
    else:
        if solver.LEF != None:
            print(f"total time: {end_construction - start + solver.solving_time:.3f}sec (construction: {end_construction - start:.3f} time on solution: {solver.solving_time:.3f})")
        else:
            print(f"timeout! {solver.timeout}")
    