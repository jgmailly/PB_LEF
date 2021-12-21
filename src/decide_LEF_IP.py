from gurobipy import *
import sys
import numpy as np

import time
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

start = time.time()
m = Model("PL1")


alloc_vars = m.addMVar(shape=n_agents*n_agents, vtype = GRB.BINARY, name = "v0")

for i in range(n_agents):
    m.addConstr(sum(alloc_vars[i*n_agents : (i+1)*n_agents]) == 1, name = f"exactly_one alloc_({i},j)")
    m.addConstr(sum(alloc_vars[i::n_agents]) == 1, name = f"exactly_one alloc_(i,{i})")
    ordObj = preferences[i]
    ordObj = [obj for obj in ordObj if len(obj) > 0] #clean the preference (it has an empty "" usually)
    for obj_i in range(len(ordObj)):
        LEF_agent_constraint = np.zeros(n_agents*n_agents)
        effective = False
        for j in range(n_agents):
            if ([agents[i],agents[j]] in social) or ([agents[j],agents[i]] in social):
                effective = True    
                LEF_agent_constraint[i*n_agents + objects.index(ordObj[obj_i])] -= 1
                for obj in ordObj[obj_i+1:]: #must be an object agent_i prefer to ordObj[i]
                    LEF_agent_constraint[j*n_agents + objects.index(obj)] = 1
        if effective:
            m.addConstr(LEF_agent_constraint @ alloc_vars >= 0, name=f"LEF agent{i} object{obj_i}")

#m.setObjective(alloc_vars, GRB.MAXIMIZE)
m.params.outputflag = 0 # mode muet
m.update()

end_writing = time.time()
print(f"time spent writing: {end_writing-start}")

m.optimize()
end = time.time()
if m.status == GRB.INFEASIBLE:
    print("no LEF Found")
else:
    print("La solution optimale est x = {} avec pour valeur de l'objectif z = {}".format(alloc_vars.x, m.objVal))
    for i in range(n_agents):
        for j in range(n_agents):
            if alloc_vars.x[i*n_agents+j] == 1:
                print(f"alloc({i}, {objects[j]})")


print(f"time spent solving: {end-end_writing}")
print(f"time spent total: {end-start}")
