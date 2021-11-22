import sys
from pysat.solvers import Glucose4


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

def parse_model(model, agents, objects, alloc_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                print(f"alloc_({agents[agent_id]},{objects[obj_id]})")

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


clauses = []
n_constraints = 0

for agent_id in range(len(agents)):
    at_least_one = []
    for obj_id in range(len(objects)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for obj2_id in range(obj_id+1, len(objects)):
            clauses.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            n_constraints += 1
    clauses.append(at_least_one)
    n_constraints += 1

for obj_id in range(len(objects)):
    at_least_one = []
    for agent_id in range(len(agents)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for agent2_id in range(agent_id+1, len(agents)):
            clauses.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]])
            n_constraints += 1
    clauses.append(at_least_one)
    n_constraints += 1
if not use_complement:
    for agent_i in agents:
        for agent_j in agents:
            if ([agent_i,agent_j] in social) or ([agent_j,agent_i] in social):
                for obj_k in objects:
                    for obj_l in objects:
                        clauses.append([-alloc_vars[agents.index(agent_i)][objects.index(obj_k)], -alloc_vars[agents.index(agent_j)][objects.index(obj_l)], pref_vars[agents.index(agent_i)][objects.index(obj_k)][objects.index(obj_l)]])
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
                clauses.append(clause)
                n_constraints += 1    


for agent in agents:
    pref_agent = preferences[agents.index(agent)]
    pb_pref_agent = encode_pref_agent(pref_agent,pref_vars,objects,agents,agent)
    clauses += pb_pref_agent[0]
    n_constraints += pb_pref_agent[1]

with Glucose4(bootstrap_with=clauses) as g:
    LEF = g.solve()
    if LEF:
        print("LEF allocation found")
        parse_model(g.get_model()[:alloc_var_id], agents, objects, alloc_vars)
    else:
        print("Not LEF allocation")
    
