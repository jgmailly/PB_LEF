import sys
import random
import networkx as nx

def print_social_network(graph,filename):
    soc_file = open(filename + ".soc",'w')
    for node in graph.nodes():
        print(node,file = soc_file)
    print("#",file = soc_file)
    for edge in graph.edges():
        print(f"{edge[0]} {edge[1]}",file = soc_file)
    soc_file.close()

def usage():
    sys.exit("Usage: python3 instance_generator.py n filename model [params...] where\n\tn is the number of agents/objects\n\tfilename is the name of the instance file\n\tmodel is the generation model: ER for Erdos-Renyi, LINE for lines, BA for Barabasi-Albert, WS for Watts-Strogatz\n\tparams are optional parameters, e.g. the probability for ER, the attachment value for BA, the number of joint nodes and the probability of rewiring for WS")

n_args = len(sys.argv)

if n_args < 4 :
    usage()

n = int(sys.argv[1])
filename = sys.argv[2]
model = sys.argv[3]

graph = None

if model == "ER":
    if n_args < 5:
        usage()
    proba = float(sys.argv[4])
    graph = nx.erdos_renyi_graph(n,proba)
elif model == "LINE":
    graph = nx.path_graph(n)
elif model == "BA":
    if n_args < 5:
        usage()
    attachment = int(sys.argv[4])
    graph=nx.barabasi_albert_graph(n,attachment)
elif model == "WS":
    if n_args < 6:
        usage()
    joint = int(sys.argv[4])
    rewiring = float(sys.argv[5])
    graph = nx.watts_strogatz_graph(n,joint,rewiring)
else:
    sys.exit(f"Model {model} unknown")

print_social_network(graph,filename)

pref_file = open(sys.argv[2] + ".pref", 'w')
objects = ["o" + str(i) for i in range(1,n+1)]

for i in range(n):
    random.shuffle(objects)
    pref_string = ""
    for obj in objects:
        pref_string += obj + " "
    print(pref_string, file = pref_file)

pref_file.close()
