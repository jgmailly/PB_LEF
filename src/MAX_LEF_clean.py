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
        self.non_lef_vars = []
        self.timeout = timeout

        self.formulation = formulation
        self.house_alloc = house_alloc if house_alloc != "auto" else "both"
        if self.formulation not in ["pairs", "complement", "consequence", "special"]:
            print(f"\"{self.formulation}\": unknown formulation (\"pairs\", \"complement\",\"consequence\",\"special\")")
            exit(-1)
        if self.house_alloc not in ["agents", "objects", "both"]:
            print(f"\"{self.house_alloc}\": unknown house_alloc (\"agents\", \"objects\", \"both\", \"auto\")")
            exit(-1)
        n_vars = 0
        alloc_var_id = 0


        for agent in agents:
            self.alloc_vars.append([])
            for _ in objects:
                n_vars += 1
                alloc_var_id += 1
                self.alloc_vars[agents.index(agent)].append(alloc_var_id)
        
        for agent in agents:
            n_vars += 1
            self.non_lef_vars.append(n_vars)
                
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
                #at_least_one.append(self.non_lef_vars[agent_id])
                house_alloc_clauses[house_alloc_clause_count] = at_least_one
                #self.clauses.append(at_least_one)
                self.clause2meaning[tuple(at_least_one)] = f"at least one object for agent {self.agents[agent_id]}"
                house_alloc_clause_count += 1
                self.n_constraints += 1

            for obj_id in range(self.n):
                for agent_id in range(self.n):
                    for agent2_id in range(agent_id+1, self.n):
                        clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent2_id][obj_id]]
                        house_alloc_clauses[house_alloc_clause_count] = clause
                        #self.clauses.append(clause)
                        self.clause2meaning[tuple(clause)] = f"only one agent for object {self.objects[obj_id]} ({self.agents[agent_id]},{self.agents[agent2_id]})"
                        house_alloc_clause_count += 1
                        self.n_constraints += 1
        
        if self.house_alloc == "objects" or self.house_alloc == "both":
            for obj_id in range(self.n):
                at_least_one = []
                for agent_id in range(self.n):
                    at_least_one.append(self.alloc_vars[agent_id][obj_id])
                    #at_least_one.append(self.non_lef_vars[agent_id])
                house_alloc_clauses[house_alloc_clause_count] = at_least_one
                #self.clauses.append(at_least_one)
                self.clause2meaning[tuple(at_least_one)] = f"at least one agent per object {self.objects[obj_id]}"
                house_alloc_clause_count += 1
                self.n_constraints += 1
            for agent_id in range(self.n):
                for obj_id in range(self.n):
                    for obj2_id in range(obj_id+1, self.n):
                        clause=[-self.alloc_vars[agent_id][obj_id], -self.alloc_vars[agent_id][obj2_id]]
                        house_alloc_clauses[house_alloc_clause_count] = clause
                        #self.clauses.append(clause)
                        self.clause2meaning[tuple(clause)] = f"only one object per agent {self.agents[agent_id]} ({self.objects[obj_id]},{self.agents[obj2_id]})"
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
            for agent1_id, agent2_id in self.social:
                ordObj1 = ordObj_pref[agent1_id]
                ordObj2 = ordObj_pref[agent2_id]        
                for objAssignedTo2 in range(len(ordObj1)):
                    for objAssignedTo1 in range(len(ordObj2)):
                        # agent1 -> agent2 or agent2 -> agent1
                        if ordObj1[objAssignedTo1] > ordObj1[objAssignedTo2]:
                            clause = [-self.alloc_vars[agent1_id][objAssignedTo1], -self.alloc_vars[agent2_id][objAssignedTo2], self.non_lef_vars[agent1_id]]
                            self.clauses.append(clause)
                            self.clause2meaning[tuple(clause)] =f"not both alloc_({self.agents[agent1_id]},{self.objects[objAssignedTo1]}) and alloc_({self.agents[agent2_id]},{self.objects[objAssignedTo2]})"
                            self.n_constraints += 1
                        if ordObj2[objAssignedTo2] > ordObj2[objAssignedTo1]:
                            clause = [-self.alloc_vars[agent1_id][objAssignedTo1], -self.alloc_vars[agent2_id][objAssignedTo2], self.non_lef_vars[agent2_id]]
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

        if self.formulation == "consequence"or self.formulation == "special":
            lef_clauses = [None]*2*len(self.social)*self.n
            lef_clause_count = 0
            for agent1_id, agent2_id in self.social:
                ordObj1 = ordObj_pref[agent1_id]
                ordObj2 = ordObj_pref[agent2_id]
                for objAssignedTo2 in range(len(ordObj1)):
                    # agent1 -> agent2
                    clause = [-self.alloc_vars[agent2_id][objAssignedTo2]]
                    meaning = f"alloc({self.agents[agent2_id]},{self.objects[objAssignedTo2]}) ->"
                    obj_possible_to_assign = []
                    for objAssignedTo1 in range(len(ordObj2)):
                        if ordObj1[objAssignedTo1] < ordObj1[objAssignedTo2]:# and ordObj2[objAssignedTo1] > ordObj2[objAssignedTo2]:
                            clause.append(self.alloc_vars[agent1_id][objAssignedTo1])
                            obj_possible_to_assign.append(self.objects[objAssignedTo1])
                    clause.append(self.non_lef_vars[agent1_id])
                    lef_clauses[lef_clause_count] = clause
                    if obj_possible_to_assign == []:
                        meaning += f" False (agent {self.agents[agent1_id]})"
                    else:
                        meaning += f" alloc({self.agents[agent1_id]},{{{'|'.join(obj_possible_to_assign)}}})"
                    self.clause2meaning[tuple(clause)] =f"not both alloc_({self.agents[agent1_id]},{self.objects[objAssignedTo1]}) and alloc_({self.agents[agent2_id]},{self.objects[objAssignedTo2]})"
                    lef_clause_count += 1
                    self.n_constraints += 1
                for objAssignedTo1 in range(len(ordObj2)): 
                    # agent2 -> agent1
                    clause = [-self.alloc_vars[agent1_id][objAssignedTo1]]
                    meaning = f"alloc({self.agents[agent1_id]},{self.objects[objAssignedTo1]}) ->"
                    obj_possible_to_assign = []
                    for objAssignedTo2 in range(len(ordObj1)):
                        if ordObj2[objAssignedTo2] < ordObj2[objAssignedTo1]:# and ordObj1[objAssignedTo2] > ordObj1[objAssignedTo1]:
                            clause.append(self.alloc_vars[agent2_id][objAssignedTo2])
                            obj_possible_to_assign.append(self.objects[objAssignedTo2])
                    clause.append(self.non_lef_vars[agent2_id])
                    lef_clauses[lef_clause_count] = clause
                    if obj_possible_to_assign == []:
                        meaning += f" False (agent {self.agents[agent2_id]})"
                    else:
                        meaning += f" alloc({self.agents[agent2_id]},{{{'|'.join(obj_possible_to_assign)}}})"
                    self.clause2meaning[tuple(clause)] =f"not both alloc_({self.agents[agent2_id]},{self.objects[objAssignedTo2]}) and alloc_({self.agents[agent1_id]},{self.objects[objAssignedTo1]})"
                    lef_clause_count += 1
                    self.n_constraints += 1
            self.clauses.extend(lef_clauses)
            #print(lef_clause_count, 2*len(social)*self.n)



    def solve(self):
        wcnf = WCNF()
        wcnf.extend([[lit for lit in clause] for clause in self.clauses])
        for agent_id in range(len(self.agents)):
            wcnf.append([-self.non_lef_vars[agent_id]], weight=1)
        g = RC2(wcnf)
        self.model = g.compute()
        self.cost = g.cost
        if g.cost == 0:
            self.LEF = True
        else:
            self.LEF = False
        g.delete()

    def print_model(self):
        print(f"number of constraints: {self.n_constraints}")
        print("LEF sol? ", self.LEF)
        if self.cost == 0:
            print("LEF allocation found")
        else:
            non_lef_agents = ""
            for agent_id in range(len(agents)):
                if self.non_lef_vars[agent_id] in self.model:
                    non_lef_agents += f"{self.agents[agent_id]} "
            print(f"solution found with {self.cost} non-LEF agent ({non_lef_agents[:-1]})")
        parse_model(self.model, self.agents, self.objects, self.alloc_vars)
        #else:
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
        for agent_id in range(len(self.agents)):
            for obj_id in range(len(self.objects)):
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
    ha = parser.add_argument_group("House alloc clauses")
    ha.add_argument("--partial", nargs = '*', help="If chosen, the solver will not use all the unicity and allocation clauses. \
                                                    If followed by 'agents' or 'objects' alone, will use only the appropriate 'at least one' and 'not both' clauses.\
                                                    otherwise, all the 'not both' clauses will be used, but only the specified alloc will be processed. \
                                                    the n next arguments will be processed by pairs \
                                                    (e.g., '--partial 0 all o1 1 o1 2' means that agent 0 has at least one from all the objects, and object o1 must get at least one agent between 1 and 2)")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-o", "--out", type=argparse.FileType('a'), help="optional file to print the output (append)")
    parser.add_argument("--mus", action="store_true", help="if set compute a mus instead of the allocation (only works if formula is unsat)")
    
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
        if len(args.partial) > 1:
            print("not implemented")
        house_alloc = args.partial[0]
    else:
        house_alloc = "both"
    start = time.time()

    solver = LEF_Solver(agents, objects, social, formulation=formulation, house_alloc=house_alloc, timeout = 150)
    solver.add_house_allocation_structure_clauses()
    solver.add_LEF_clauses()
    end_construction = time.time()
    
    if args.mus:
        solver.computeMUS()
        exit()
    solver.solve()
    if solver.LEF != None:
        solver.print_model()
        if solver.LEF:
            solver.check()
            print("check passed")
    