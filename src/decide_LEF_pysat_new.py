import sys
from pysat.solvers import Glucose4
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
    #parse_unsat_pref(model, agents, objects, pref_vars)

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
soft_clauses = []
for agent_id in range(len(agents)):
    at_least_one = []
    for obj_id in range(len(objects)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for obj2_id in range(obj_id+1, len(objects)):
            wcnf.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            wcnf2.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent_id][obj2_id]])
            n_constraints += 1
    wcnf.append(at_least_one,weight=1)
    soft_clauses.append([lit for lit in at_least_one])
    n_constraints += 1

for obj_id in range(len(objects)):
    at_least_one = []
    for agent_id in range(len(agents)):
        at_least_one.append(alloc_vars[agent_id][obj_id])
        for agent2_id in range(agent_id+1, len(agents)):
            wcnf.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]])
            wcnf2.append([-alloc_vars[agent_id][obj_id], -alloc_vars[agent2_id][obj_id]])
            n_constraints += 1
    wcnf.append(at_least_one,weight=1)
    soft_clauses.append([lit for lit in at_least_one])
    n_constraints += 1


for agent_i in agents:
    ordObj = preferences[agents.index(agent_i)]
    ordObj = [obj for obj in ordObj if len(obj) > 0] #clean the preference (it has an empty "" usually)
    for agent_j in agents:
        if ([agent_i,agent_j] in social) or ([agent_j,agent_i] in social):    
            ordObj2 = preferences[agents.index(agent_j)]
            ordObj2 = [obj for obj in ordObj2 if len(obj) > 0] #clean the preference (it has an empty "" usually)
            for i in range(len(ordObj)):
                clause = [-alloc_vars[agents.index(agent_j)][objects.index(ordObj[i])]]
                for obj in ordObj[:i]: #must be an object agent_i prefer to ordObj[i]
                    #if obj in ordObj2[ordObj2.index(ordObj[i])+1:]: #must not be an object agent_j prefer to ordObj[i]
                    clause.append(alloc_vars[agents.index(agent_i)][objects.index(obj)])
                wcnf.append(clause, weight=1)
                soft_clauses.append([lit for lit in clause])
                n_constraints += 1    


# for agent in agents:
#     pref_agent = preferences[agents.index(agent)]
#     pb_pref_agent = encode_pref_agent(pref_agent,pref_vars,objects,agents,agent)
#     wcnf.extend(pb_pref_agent[0])
#     wcnf2.extend([[lit for lit in clause] for clause in pb_pref_agent[0]])
#     n_constraints += pb_pref_agent[1]

print(n_constraints, len(wcnf.soft))
mus = None
print("Force an allocation? e.g. '0 o2' =>  alloc(0,o2)")
response = input().split()
forced_object = None
if len(response) == 2:
    wcnf.append([alloc_vars[agents.index(response[0])][objects.index(response[1])]])
    wcnf2.append([alloc_vars[agents.index(response[0])][objects.index(response[1])]])
    forced_object = (agents.index(response[0]), objects.index(response[1]))
response = input("Solution or MUS? [sol|mus]: ")
if response.lower() == "sol":
    with Glucose4(bootstrap_with= wcnf.hard + wcnf.soft) as g:
        LEF = g.solve()
        model = g.get_model()
        if LEF:
            print("LEF allocation found")
            parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
            #print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")
        else:
            print("No LEF allocation")
            #parse_model(model[:alloc_var_id], agents, objects, alloc_vars, pref_vars)
            #print(f"Solution with {rc2.cost} unsatisfied soft clause{'s' if rc2.cost > 1 else ''}")
    exit(0)
                

elif response.lower() == "mus":
    musx = MUSX(wcnf, verbosity=0)
    mus = musx.compute()
    if mus == None:
        print("Solution Found.")
        exit(0)

else:
    exit(0)
print(f"len mus: {len(mus)}")
clause_mus = []
for i in range(len(mus)):
    if i not in []:
        clause_mus.append(soft_clauses[mus[i]-1])




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
    
    if ids == []: #False, so the clause is a contradiction
        return result, None, set_agent, set_obj

    return result, (ids[0], ids[1]) if len(ids)==2 else (ids[0],), set_agent, set_obj

def decode_mus(clause_mus):
    ids = set()
    two = 0
    one = 0
    set_ag = set()
    set_ob = set()
    for clause in clause_mus:
        ids_clause, set_agent, set_obj  = decode_clause(clause)
        set_ag = set_ag.union(set_agent)
        set_ob = set_ob.union(set_obj)
        if ids_clause != None and len(ids_clause) == 2:
            two += 1
        elif ids_clause != None and len(ids_clause) == 1:
            one += 1
        ids.add(ids_clause)
        
    return ids, one, two, set_ag, set_ob


ids, one, two, set_ag, set_obj  = decode_mus(clause_mus)
print(one, two, set_ag, set_obj )
print()

def reduce_MUS(clause_mus):
    acc = []
    ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
    clause_mus = [clause for clause in clause_mus if (len(clause)>1 or all(lit>0 for lit in clause))]
    while len(ones)>0:
        for one_clause in ones:
            for i in range(len(clause_mus)):
                if -one_clause[0] in clause_mus[i]:
                    clause_mus[i].remove(-one_clause[0])
        print(len(clause_mus), clause_mus)
        acc.extend(ones)
        ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
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
    print(one, two, set_ag, set_obj)
    print()

print("Performing resolutions to reduce the MUS")
cl ,acc = reduce_MUS(clause_mus)
cl.extend(acc)
ids, one, two, set_ag, set_obj = decode_mus(cl)
print(one, two, set_ag, set_obj)
