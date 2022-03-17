import sys
from pysat.solvers import Glucose4, Minisat22
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.examples.mcsls import MCSls
from pysat.formula import WCNF
import matplotlib.pyplot as plt
import random
import networkx as nx
import time

from collections import defaultdict


import graphviz

def parse_tgf(social_file):
    with open(social_file) as soc_file:
        social_lines = soc_file.read().splitlines()

    end_agents = False
    agents = []
    social = []
    for soc_line in social_lines:
        if soc_line != "#":
            if not end_agents:
                agents.append(soc_line)
            else:
                social.append(parse_social_line(soc_line))
        else:
            end_agents = True
    return agents, social

def parse_preference_line(pref_line):
    return pref_line.split(" ")

def parse_social_line(soc_line):
    return soc_line.split(" ")

def get_objects_from_preferences(preferences):
    objects = []
    for pref in preferences:
        for obj in pref:
            if (obj not in objects) and (len(obj) >= 1):
                objects.append(obj)
    return objects


def encode_pref_agent(pref_agent,pref_vars,objects,agents,agent):
    pref_index = 0
    n_constraints = 0
    clauses = []

    for obj_k in objects:
        for obj_l in objects:
            if pref_agent.index(obj_k) < pref_agent.index(obj_l):
                # The agent prefers obj_k to obj_l
                clauses.append([pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]])
                n_constraints += 1
            else:
                clauses.append([-pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]])
                n_constraints += 1

    return [clauses,n_constraints]

def parse_model(model, agents, objects, alloc_vars, pref_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                print(f"alloc_({agents[agent_id]},{objects[obj_id]})")
    #parse_unsat_pref(model, agents, objects, pref_vars)

def parse_unsat_pref(model, agents, objects, pref_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            for obj2_id in range(len(objects)):
                if pref_vars[agent_id][obj_id][obj2_id] in model:
                    print(f"pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]})")



def decode_clause(clause):
    result, ids, set_agent, set_obj = parse_better(clause, agents, objects, alloc_vars, pref_vars)
    print(result) if len(result) != 0 else print("False !")
    return ids, set_agent, set_obj 


def parse(model, agents, objects, alloc_vars, pref_vars):
    result = ""
    ids = []
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in model:
                ids.append([agent_id, obj_id])
                result += f"not alloc_({agents[agent_id]},{objects[obj_id]}), "
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                ids.append([agent_id, obj_id])
                result += f"alloc_({agents[agent_id]},{objects[obj_id]}), "
    
    return result, ids

def parse_better(model, agents, objects, alloc_vars, pref_vars):
    result = ""
    ids = []
    set_obj = set()
    set_agent = set()
    
    #if it is a preference clause
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in model:
                ids.append(agent_id)
                result += f"alloc_({agents[agent_id]},{objects[obj_id]}) => "
                set_agent.add(agent_id)
                set_obj.add(obj_id)
    
    for agent_id in range(len(agents)):
        started = False
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                if not started:
                    ids.append(agent_id)
                    result += f"alloc_({agents[agent_id]}, {{"
                    set_agent.add(agent_id)
                    started = True
                result += f"{objects[obj_id]},"
                
                set_obj.add(obj_id)
        if started:
            result += "})"
            started = False
    
    

    return result, (ids[0], ids[1]) if len(ids)==2 else (ids[0],), set_agent, set_obj

def print_at_least_one(set_agent, set_obj):
    if len(set_obj) == 1:
        obj_id = list(set_obj)[0]
        toprint = f"Give {objects[obj_id]:3} to one of "
        for agent_id in range(len(agents)):
            if agent_id in set_agent:
                toprint += f"{agents[agent_id]} "
            else:
                toprint += " "*(1+len(str(agents[agent_id])))
        toprint = toprint[:-1]
        print(toprint)
    elif len(set_agent) == 1:
        agent_id = list(set_agent)[0]
        toprint = f"Give to {agents[agent_id]:2} one of "
        for obj_id in range(len(objects)):
            if obj_id in set_obj:
                toprint += f"{objects[obj_id]} "
            else:
                toprint += " "*(1+len(str(objects[obj_id])))
        toprint = toprint[:-1]
        print(toprint)
    
def print_not_both(clause):
    to_print = "not both "
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in clause:
                to_print += f"alloc_({agents[agent_id]},{objects[obj_id]}) and "
    to_print = to_print[:-5]
    print(to_print) 

def decode_mus(clause_mus, skip_ones=False):
    ids = set()
    two = 0
    one = 0
    set_ag = set()
    set_ob = set()
    for clause in clause_mus:
        if clause == []:
            print("False !")
            continue
        elif all([lit > 0 for lit in clause]):
            set_agent = set()
            set_obj = set()
            for agent_id in range(len(agents)):
                for obj_id in range(len(objects)):
                    if alloc_vars[agent_id][obj_id] in clause:
                        set_agent.add(agent_id)
                        set_obj.add(obj_id)
            set_ag = set_ag.union(set_agent)
            set_ob = set_ob.union(set_obj)
            print_at_least_one(set_agent, set_obj)
        elif len(clause) == 2 and all([lit < 0 for lit in clause]):
            print_not_both(clause)
        else:
            if skip_ones and len(clause) == 1:
                one += 1
                continue
            ids_clause, set_agent, set_obj  = decode_clause(clause)
            set_ag = set_ag.union(set_agent)
            set_ob = set_ob.union(set_obj)
            if ids_clause != None and len(ids_clause) == 2:
                two += 1
            elif ids_clause != None and len(ids_clause) == 1:
                one += 1
            ids.add(ids_clause)
        
    return ids, one, two, set_ag, set_ob


if len(sys.argv) != 3:
    sys.exit("Usage: python3 solve_LFE.py <preferences_file> <social_file>")

preferences_file = sys.argv[1]
social_file = sys.argv[2]


preferences = []

with open(preferences_file) as pref_file:
    preferences_lines = pref_file.read().splitlines()

for pref_line in preferences_lines:
    preferences.append(parse_preference_line(pref_line))


agents, social = parse_tgf(social_file)
# with open(social_file) as soc_file:
#     social_lines = soc_file.read().splitlines()

# for soc_line in social_lines:
#     social.append(parse_social_line(soc_line))


objects = get_objects_from_preferences(preferences)
#agents = get_agents_from_social(social)

if len(objects) != len(agents):
    sys.exit(f"The number of agents ({len(agents)}) must be the same as the number of objects ({len(objects)}).")


n_agents = len(agents)

alloc_vars = []
n_vars = 0
alloc_var_id = 0

#response = input("remove some agent?:")
#
#if response != "":
#    response = [int(x) for x in response.split()]
#else:
#    response = []
response = []

start = time.time()

lit_meaning = dict()

for agent in agents:
    alloc_vars.append([])
    for obj in objects:
        n_vars += 1
        alloc_var_id += 1
        alloc_vars[agents.index(agent)].append(alloc_var_id)
        lit_meaning[alloc_var_id] = f"alloc({agent},{obj})"

pref_var_id = 0

pref_vars = []
for agent in agents:
    pref_vars.append([])
    for obj_k in objects:
        pref_vars[agents.index(agent)].append([])
        for obj_l in objects:
            n_vars += 1
            pref_var_id += 1
            pref_vars[agents.index(agent)][objects.index(obj_k)].append(alloc_var_id + pref_var_id)
            
            lit_meaning[alloc_var_id + pref_var_id] = f"pref({agent}|{obj_k}<{obj_l})"



clause2meaning = dict()

wcnf = WCNF()
#wcnf2 = WCNF()
n_constraints = 0
soft_clauses = []

print("Force an allocation? e.g. '0 o2' =>  alloc(0,o2)")
response = input().split()
forced_object = None
forced_clause = None
if len(response) == 2:
    clause = [alloc_vars[agents.index(response[0])][objects.index(response[1])]]
    clause2meaning[tuple(clause)] = f"forced allocation of {response[0]} {response[1]}"
    wcnf.append(clause)
    forced_clause = [lit for lit in clause]
    forced_object = (agents.index(response[0]), objects.index(response[1]))
    n_constraints += 1


for agent_id in range(len(agents)):
    if forced_object != None and agent_id == forced_object[0]: continue
    at_least_one = []
    for obj_id in range(len(objects)):
        if forced_object != None and obj_id == forced_object[1]: continue
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for obj2_id in range(obj_id+1, len(objects)):
            if forced_object != None and obj2_id == forced_object[1]: continue
            
            clause = [-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]]
            wcnf.append(clause, weight=1)
            soft_clauses.append([lit for lit in clause])
            
            clause2meaning[tuple(clause)] = f"only one object for agent {agents[agent_id]} ({objects[obj_id]},{objects[obj2_id]})"
    
            
            #wcnf2.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            n_constraints += 1
    wcnf.append(at_least_one,weight=1)
    soft_clauses.append([lit for lit in at_least_one])
    clause2meaning[tuple(at_least_one)] = f"at least one object for agent {agents[agent_id]}"
    
    n_constraints += 1

for obj_id in range(len(objects)):
    if forced_object != None and obj_id == forced_object[1]: continue
    at_least_one = []
    for agent_id in range(len(agents)):
        if forced_object != None and agent_id == forced_object[0]: continue
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for agent2_id in range(agent_id+1, len(agents)):
            if forced_object != None and agent2_id == forced_object[0]: continue
            clause=[-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]]
            wcnf.append(clause,weight=1)
            soft_clauses.append([lit for lit in clause])


            clause2meaning[tuple(clause)] = f"only one agent for object {objects[obj_id]} ({agents[agent_id]},{agents[agent2_id]})"

            n_constraints += 1
    wcnf.append(at_least_one,weight=1)
    soft_clauses.append([lit for lit in at_least_one])

    clause2meaning[tuple(at_least_one)] = f"at least one agent for object {objects[obj_id]}"
    

    n_constraints += 1

ordObj_pref = [None]*len(agents)
for agent_id in range(len(agents)):
    objId2prefLevel = [None]*len(objects)
    prefs_agent_i = preferences[agent_id]
    for i in range(len(objects)):
        objId2prefLevel[objects.index(prefs_agent_i[i])] = i
    #print(objId2prefLevel)
    ordObj_pref[agent_id] = objId2prefLevel

for agent1_id in range(len(agents)):
    ordObj1 = ordObj_pref[agent1_id]
    for agent2_id in range(len(agents)):   
        if ([agents[agent1_id],agents[agent2_id]] in social) or ([agents[agent2_id],agents[agent1_id]] in social):    
            ordObj2 = ordObj_pref[agent2_id]
            for objAssignedTo2 in range(len(ordObj1)):
                clause = [-alloc_vars[agent2_id][objAssignedTo2]]
                meaning = f"alloc({agents[agent2_id]},{objects[objAssignedTo2]}) ->"
                obj_possible_to_assign = []
                for objAssignedTo1 in range(len(ordObj2)):
                    if ordObj1[objAssignedTo1] < ordObj1[objAssignedTo2] and ordObj2[objAssignedTo1] > ordObj2[objAssignedTo2]:
                        clause.append(alloc_vars[agent1_id][objAssignedTo1])
                        obj_possible_to_assign.append(objects[objAssignedTo1]) 
                wcnf.append(clause, weight=1)
                soft_clauses.append([lit for lit in clause])
                if obj_possible_to_assign == []:
                    meaning += f" False (agent {agents[agent1_id]})"
                else:
                    meaning += f" alloc({agents[agent1_id]},{{{'|'.join(obj_possible_to_assign)}}})"
                clause2meaning[tuple(clause)] = meaning#f"{agents[agent1_id]}-{agents[agent2_id]} preferences consequence"

                n_constraints += 1    


# for agent in agents:
#     pref_agent = preferences[agents.index(agent)]
#     pb_pref_agent = encode_pref_agent(pref_agent,pref_vars,objects,agents,agent)
#     wcnf.extend(pb_pref_agent[0])
#     wcnf2.extend([[lit for lit in clause] for clause in pb_pref_agent[0]])
#     n_constraints += pb_pref_agent[1]


end_writing = time.time()
print(f"time spent writing: {end_writing - start}")

print(n_constraints, len(wcnf.soft))
mus = None



response = input("Solution or MUS? [sol|mus]: ")

start_thinking = time.time()

if response.lower() == "sol":
    #with Glucose4(bootstrap_with= wcnf.hard + wcnf.soft) as g:
    with Minisat22(bootstrap_with= wcnf.hard + wcnf.soft) as g:
        LEF = g.solve()
        
        end = time.time()
        model = g.get_model()
        if LEF:
            print("LEF allocation found")
            parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
            #print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")
        else:
            print("No LEF allocation")
            #parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
            #print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")

        
    print(f"time spent finding solution: {end - start_thinking}")
    print(f"time spent in total: {end - start_thinking + end_writing - start}")

    exit(0)
                

elif response.lower() == "mus":
    musx = MUSX(wcnf, verbosity=0)
    mus = musx.compute()
    if mus == None:
        print("Solution Found.")
        exit(0)


elif response.lower() == "mcs":
    print("here")
    mcsls = MCSls(wcnf,use_cld=True, solver_name='g3')
    print("here")
    mcs = mcsls.compute()
    clause_mcs = []
    for i in range(len(mcs)):
        if i not in []:
            clause_mcs.append(soft_clauses[mcs[i]-1])
    print(clause_mcs)
    decode_mus(clause_mcs)

else:
    exit(0)

print(f"len mus: {len(mus)}")
clause_mus = []
for i in range(len(mus)):
    if i not in []:
        clause_mus.append(soft_clauses[mus[i]-1])
if forced_clause != None: 
    clause_mus.append(forced_clause)




ids, one, two, set_ag, set_obj  = decode_mus(clause_mus)
#print(one, two, set_ag, set_obj )
print()

def reduce_MUS(clause_mus):
    acc = []
    ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
    clause_mus = [clause for clause in clause_mus if (len(clause)>1 or all(lit>0 for lit in clause))]
    while len(ones)>0:
        for one_clause in ones:
            for i in range(len(clause_mus)):
                if -one_clause[0] in clause_mus[i]:
                    tmp = clause2meaning[tuple(clause_mus[i])] 
                    clause_mus[i].remove(-one_clause[0])
                    clause2meaning[tuple(clause_mus[i])] = tmp
        #print(len(clause_mus), clause_mus)
        acc.extend(ones)
        ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
        ##FORCE ASSIGNEMENT WHEN JUST POSITIVE
        #forced_assginment = [clause for clause in clause_mus if (len(clause)==1 and all(lit>0 for lit in clause))]
        clause_mus = [clause for clause in clause_mus if(len(clause)>1 or all(lit>0 for lit in clause))]
    return clause_mus, acc


if forced_object != None:
    print("We forced an allocation, we can remove impossible assignments")
    for i in range(len(objects)): # remove impossible objects for forced agent
        if i != forced_object[1]:
            for clause in clause_mus:
                if alloc_vars[forced_object[0]][i] in clause:
                    clause.remove(alloc_vars[forced_object[0]][i])
    for i in range(len(agents)): # remove impossible object for non forced agents
        if i != forced_object[0]:
            for clause in clause_mus:
                if alloc_vars[i][forced_object[1]] in clause:
                    clause.remove(alloc_vars[i][forced_object[1]])
    ids, one, two, set_ag, set_obj = decode_mus(clause_mus)
    #print(one, two, set_ag, set_obj)
    print()

def draw_other_dag(clause_mus, name):
    # TODO

    G = graphviz.Digraph(name)

    at_least_ones = [clause for clause in clause_mus if all((lit>0 for lit in clause))]
    not_boths = [clause for clause in clause_mus if len(clause)==2 and clause[0] < 0 and clause[1] < 0]
    impossibles = [clause for clause in clause_mus if len(clause)==1 and clause[0] < 0]
    chaineds = [clause for clause in clause_mus if not all((lit>0 for lit in clause)) and
                                                   not (len(clause)==2 and clause[0] < 0 and clause[1] < 0) and
                                                   not (len(clause)==1 and clause[0] < 0)]
    


    # first accumulate color    
    colors = ["red3","blue3","yellowgreen","dodgerblue","yellow","green", "violet"]
    lit2color = defaultdict(lambda:[])
    for i,clause in enumerate(at_least_ones):
        color = colors[i]
        for lit in clause:
            lit2color[lit].append(color) 
    
    for clause in at_least_ones:
        for lit in clause:
            print(lit2color[lit])
            if len(lit2color[lit]) > 1:
                G.attr('node', shape='circle',  style='wedged',fillcolor=":".join(lit2color[lit]), fontcolor="white")
            else:
                G.attr('node', shape='circle',  style='filled',fillcolor=lit2color[lit][0], fontcolor="white")
            G.node(lit_meaning[lit])

    if len(impossibles) != 0:
        G.node('False',shape='circle', style='filled',fillcolor="black", fontcolor="white")
    for clause in impossibles:
        G.attr('node', shape='circle', style='solid', fontcolor="black")
    
        G.edge(lit_meaning[-clause[0]], "False", label=clause2meaning[tuple(clause)], fontsize='10pt')

    
    
    for clause in not_boths:
        G.attr("edge",dir='none', style='dashed')
        G.attr('node', shape='circle',  style='solid', fontcolor="black")
        G.node(lit_meaning[-clause[0]])
        G.node(lit_meaning[-clause[1]])
        G.edge(lit_meaning[-clause[0]],lit_meaning[-clause[1]])
    

    for i,clause in enumerate(chaineds):
        G.attr('node', shape='circle',  style='solid', fontcolor="black")
        G.attr('edge',dir='forward', style='solid')
        lit = -clause[0]
        G.node(lit_meaning[lit])
        for consequence in clause[1:]:
            G.attr('edge',dir='forward', style='solid', color=colors[i%len(colors)], label=clause2meaning[tuple(clause)])
            G.node(lit_meaning[consequence])
            G.edge(lit_meaning[lit], lit_meaning[consequence])

    
    G.view()


def draw_dag(clause_mus):
    G = nx.DiGraph()

    restriction_clauses = []

    for clause in clause_mus:
        if all(lit > 0 for lit in clause):
            G.add_node(clause[0], label=lit_meaning[clause[0]])
        else:
            restriction_clauses.append(clause)


    def reduce_clauses(clauses, nodes):
        new_clauses = []
        new_nodes = []
        for clause in clauses:
            new_clause = [lit for lit in clause if -lit not in nodes]
            
        return new_clauses, new_nodes
    
    

    new_nodess = []
    while True:
        for node in G.nodes:
            restriction_clauses, new_nodes = reduce_clauses(restriction_clauses, node)
            new_nodess.extend(new_nodes)
        if len(new_nodess) == 0:
            return
    
    
    
    last_len =0
    curr_len =len(G.nodes)
    while last_len != curr_len:
        
        #print(curr_len)
        nodes = list(G.nodes)
        last_len = curr_len

        for node in nodes:
            print("hey, ",node)
            for clause in restriction_clauses:
                if -node in clause:
                    pass
        curr_len = len(G.nodes)
                            

    pos = nx.spring_layout(G,k = 5.0, iterations=50)
    #pos = nx.random_layout(G)
    #pos = nx.kamada_kawai_layout(G)
    #pos = nx.spectral_layout(G)
    #pos = nx.shell_layout(G)
    #pos = nx.spring_layout(G, pos=nx.planar_layout(G), k = 10.0, iterations=50, dim=3)
    
    nx.draw(G, pos)
    
    plt.show()



draw_other_dag(clause_mus, "Full MUS DAG")

print("Performing resolutions to reduce the MUS")
cl ,acc = reduce_MUS(clause_mus)

ids, one, two, set_ag, set_obj = decode_mus(cl+ acc,True)
print(one, two, set_ag, set_obj)
end = time.time()
draw_other_dag(cl,"reduced MUS DAG")

print(f"time spent finding solution: {end - start_thinking}")
print(f"time spent in total: {end - start_thinking + end_writing - start}")
