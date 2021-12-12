import sys
#from pysat.solvers import Glucose4
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.formula import WCNF

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
    parse_unsat_pref(model, agents, objects, pref_vars)

def parse_unsat_pref(model, agents, objects, pref_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            for obj2_id in range(len(objects)):
                if pref_vars[agent_id][obj_id][obj2_id] in model:
                    print(f"pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]})")

if len(sys.argv) != 4:
    sys.exit("Usage: python3 solve_LFE.py <preferences_file> <social_file> <use_complement>")

preferences_file = sys.argv[1]
social_file = sys.argv[2]
use_complement = True if sys.argv[3] == "True" else False


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

for agent in agents:
    alloc_vars.append([])
    for obj in objects:
        n_vars += 1
        alloc_var_id += 1
        alloc_vars[agents.index(agent)].append(alloc_var_id)

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

wcnf = WCNF()
wcnf2 = WCNF()
n_constraints = 0

for agent_id in range(len(agents)):
    at_least_one = []
    for obj_id in range(len(objects)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for obj2_id in range(obj_id+1, len(objects)):
            wcnf.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            wcnf2.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            n_constraints += 1
    wcnf.append(at_least_one)
    wcnf2.append([lit for lit in at_least_one])
    n_constraints += 1

for obj_id in range(len(objects)):
    at_least_one = []
    for agent_id in range(len(agents)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for agent2_id in range(agent_id+1, len(agents)):
            wcnf.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]])
            wcnf2.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]])
            n_constraints += 1
    wcnf.append(at_least_one)
    wcnf2.append([lit for lit in at_least_one])
    n_constraints += 1

soft_clauses = []

if not use_complement:
    for agent_i in agents:
        for agent_j in agents:
            if ([agent_i,agent_j] in social) or ([agent_j,agent_i] in social):
                for obj_k in objects:
                    for obj_l in objects:
                        wcnf.append([-alloc_vars[agents.index(agent_i)][objects.index(obj_k)], -alloc_vars[agents.index(agent_j)][objects.index(obj_l)], -pref_vars[agents.index(agent_i)][objects.index(obj_l)][objects.index(obj_k)]], weight=1)
                        soft_clauses.append([-alloc_vars[agents.index(agent_i)][objects.index(obj_k)], -alloc_vars[agents.index(agent_j)][objects.index(obj_l)], -pref_vars[agents.index(agent_i)][objects.index(obj_l)][objects.index(obj_k)]])
                        #wcnf.append([-alloc_vars[agents.index(agent_i)][objects.index(obj_k)], -alloc_vars[agents.index(agent_j)][objects.index(obj_l)], pref_vars[agents.index(agent_i)][objects.index(obj_k)][objects.index(obj_l)]], weight=1)
                        #soft_clauses.append([-alloc_vars[agents.index(agent_i)][objects.index(obj_k)], -alloc_vars[agents.index(agent_j)][objects.index(obj_l)], pref_vars[agents.index(agent_i)][objects.index(obj_k)][objects.index(obj_l)]])
                        
                        n_constraints += 1
else:
    unknown_agents = dict()
    for agent_i in agents:
        unknown_agents[agent_i] = list()
    for agent_i in agents:
        for agent_j in agents:
            if (agent_i != agent_j) and not (([agent_i,agent_j] in social) or ([agent_j,agent_i] in social)):
                unknown_agents[agent_i].append(agent_j)
    #for agent_i in agents:
    #    print(unknown_agents[agent_i])
    for obj_k in objects:
        for obj_l in objects:
            for agent_i in agents:
                clause = []
                clause += [-pref_vars[agents.index(agent_i)][objects.index(obj_k)][objects.index(obj_l)], -alloc_vars[agents.index(agent_i)][objects.index(obj_l)]]
                for agent_j in unknown_agents[agent_i]:
                    clause.append(alloc_vars[agents.index(agent_j)][objects.index(obj_k)])
                wcnf.append(clause, weight=1)
                soft_clauses.append([lit for lit in clause])
                n_constraints += 1    


for agent in agents:
    pref_agent = preferences[agents.index(agent)]
    pb_pref_agent = encode_pref_agent(pref_agent,pref_vars,objects,agents,agent)
    wcnf.extend(pb_pref_agent[0])
    wcnf2.extend([[lit for lit in clause] for clause in pb_pref_agent[0]])
    n_constraints += pb_pref_agent[1]

wcnf2.extend(soft_clauses, weights=[1]*len(soft_clauses))

print(n_constraints, len(wcnf.soft))
mus = None
print("Force an allocation? e.g. '0 o2' =>  alloc(0,o2)")
response = input().split()
if len(response) == 2:
    wcnf.append([alloc_vars[agents.index(response[0])][objects.index(response[1])]])
    wcnf2.append([alloc_vars[agents.index(response[0])][objects.index(response[1])]])
with RC2(wcnf) as rc2:
    model = rc2.compute()
    if rc2.cost == 0:
        print("LEF allocation found")
        parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
        print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")
    else:
        print("No LEF allocation")
        parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
        print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")
        #rc2.get_core()
        #print(rc2.core_sels)
        
        if input("Compute MUS? [Y]")=="Y":
            musx = MUSX(wcnf2, verbosity=0)
            print(wcnf2.soft[0], wcnf.soft[0])
            mus = musx.compute()

if mus == None:
    exit(0)
print(f"len mus: {len(mus)}")
clause_mus = []
for i in range(len(mus)):
    clause_mus.append(soft_clauses[mus[i]-1])


def decode_mus(clause_mus, use_complement=use_complement):
    ids = []
    if use_complement:
        for clause in clause_mus:
            ids.append(decode_comp_clause(clause))
    else:
        for clause in clause_mus:
            ids.append(decode_not_comp_clause(clause))
    return ids


def decode_comp_clause(clause):
    result, ids = parse(clause, agents, objects, alloc_vars, pref_vars)
    print(result)
    return ids



def decode_not_comp_clause(clause):
    result, ids = parse(clause, agents, objects, alloc_vars, pref_vars)
    print(result)
    return ids


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
    # for agent_id in range(len(agents)):
    #     for obj_id in range(len(objects)):
    #         for obj2_id in  range(len(objects)):
    #             if -pref_vars[agent_id][obj_id][obj2_id] in model:
    #                 ids.append([agent_id, obj_id, obj2_id])
    #                 result += f"not pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]}), "
    # for agent_id in range(len(agents)):
    #     for obj_id in range(len(objects)):
    #         for obj2_id in  range(len(objects)):
    #             if pref_vars[agent_id][obj_id][obj2_id] in model:
    #                 ids.append([agent_id, obj_id, obj2_id])
    #                 result += f"pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]}), "
    
    return result, ids

ids = decode_mus(clause_mus)
#ids = [i[-1] for i in ids]
#print(ids)
#print(objects[ids[0][1]])
