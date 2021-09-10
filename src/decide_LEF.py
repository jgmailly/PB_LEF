import sys
import subprocess

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

# def get_agents_from_social(social):
#     agents = []
#     for link in social:
#         for agent in link:
#             if agent not in agents:
#                 agents.append(agent)
#     return agents

def decode_literal(alloc_vars,pref_vars,literal,objects,agents):
    for alloc_agent in alloc_vars:
        if literal in alloc_agent:
            agent = agents[alloc_vars.index(alloc_agent)]
            obj = objects[alloc_agent.index(literal)]
            return f"alloc_({agent},{obj})"

    for pref_agent in pref_vars:
        for pref_agent_obj_k in pref_agent:
            if literal in pref_agent_obj_k:
                agent = agents[pref_vars.index(pref_agent)]
                obj_k = objects[pref_agent.index(pref_agent_obj_k)]
                obj_l = objects[pref_agent_obj_k.index(literal)]
                return f"pref_{agent}^({obj_k},{obj_l})"

def decode_model(alloc_vars,pref_vars,model,objects,agents):
    result = []
    for literal in model:
        result.append(decode_literal(alloc_vars,pref_vars,literal,objects,agents))
    return result

def encode_pref_agent(pref_agent,pref_vars,objects,agents,agent):
    ### TO DO: Transitive closure
    pref_index = 0
    n_constraints = 0
    pb_encoding = ""

    for obj_k in objects:
        for obj_l in objects:
            if pref_agent.index(obj_k) < pref_agent.index(obj_l):
                # The agent prefers obj_k to obj_l
                pb_encoding += f"1 {pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]} >= 1;\n"
                n_constraints += 1
            else:
                pb_encoding += f"1 {pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]} = 0;\n"
                n_constraints += 1

    return [pb_encoding,n_constraints]

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

for agent in agents:
    alloc_vars.append([])
    for obj in objects:
        n_vars += 1
        alloc_vars[agents.index(agent)].append("x" + str(n_vars))

pref_vars = []
for agent in agents:
    pref_vars.append([])
    for obj_k in objects:
        pref_vars[agents.index(agent)].append([])
        for obj_l in objects:
            n_vars += 1
            pref_vars[agents.index(agent)][objects.index(obj_k)].append("x" + str(n_vars))



pb_encoding = ""
n_constraints = 0

for agent in agents:
    alloc = ""
    cpt = 1
    for obj in objects:
        alloc += f"1 {alloc_vars[agents.index(agent)][objects.index(obj)]}"
        if cpt < len(objects):
            alloc += " +"
        cpt += 1
    alloc += " = 1;"
    pb_encoding += alloc + "\n"
    n_constraints += 1

for obj in objects:
    alloc = ""
    cpt = 1
    for agent in agents:
        alloc += f"1 {alloc_vars[agents.index(agent)][objects.index(obj)]}"
        if cpt < len(agents):
            alloc += " +"
        cpt += 1
    alloc += " = 1;"
    pb_encoding += alloc + "\n"
    n_constraints += 1

for agent_i in agents:
    for agent_j in agents:
        if ([agent_i,agent_j] in social) or ([agent_j,agent_i] in social):
            for obj_k in objects:
                for obj_l in objects:
                    pb_encoding += f"1 ~{alloc_vars[agents.index(agent_i)][objects.index(obj_k)]} +1 ~{alloc_vars[agents.index(agent_j)][objects.index(obj_l)]} +1 {pref_vars[agents.index(agent_i)][objects.index(obj_k)][objects.index(obj_l)]} >= 1;\n"
                    n_constraints += 1

#print("Preferences:", preferences)
for agent in agents:
    pref_agent = preferences[agents.index(agent)]
    pb_pref_agent = encode_pref_agent(pref_agent,pref_vars,objects,agents,agent)
    pb_encoding += pb_pref_agent[0]
    n_constraints += pb_pref_agent[1]

tmp_file = open('tmp.opb','w')
print(f"* #variable= {n_vars} #constraint= {n_constraints}", file = tmp_file)
print(pb_encoding, file = tmp_file)



tmp_file.close()
process = subprocess.run(["java", "-jar", "sat4j-pb.jar", "tmp.opb"], capture_output=True,encoding="UTF-8")

#print(process.stdout)
pb_out = process.stdout.split("\n")
model = []
has_solution = False
for line in pb_out:
    if line.startswith("v "):
        #print(line)
        has_solution = True
        model = line.split(" ")[1:]

#print(model)
#print(decode_model(alloc_vars,pref_vars,model,objects,agents))
if has_solution:
    allocation = []
    for literal in decode_model(alloc_vars,pref_vars,model,objects,agents):
        if literal != None and literal.startswith("alloc"):
            allocation.append(literal)
    for alloc in allocation:
        print(alloc)
else:
    print("No LEF allocation")
