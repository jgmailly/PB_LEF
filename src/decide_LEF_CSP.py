from constraint import *
import sys

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

problem = Problem()
problem.addVariables(agents, objects)
n_constraints = 0

problem.addConstraint(AllDifferentConstraint())
n_constraints+=1

def lamb(ordObj):
    def inner(i,j):
        return i in ordObj[:ordObj.index(j)]
    return inner

for agent_i in agents:
    ordObj = preferences[agents.index(agent_i)]
    ordObj = [obj for obj in ordObj if len(obj) > 0] #clean the preference (it has an empty "" usually)
    for agent_j in agents:
        if ([agent_i,agent_j] in social) or ([agent_j,agent_i] in social):
            problem.addConstraint(lamb(ordObj), [agent_i, agent_j])
            n_constraints+=1

print(problem.getSolution(), n_constraints)
                            