import sys

from collections import defaultdict

import networkx as nx
import graphviz

def parse_tgf(social_file):
    social_lines = social_file.read().splitlines()

    end_agents = False
    agents = []
    social = []
    number_of_edges = 0
    for soc_line in social_lines:
        if soc_line != "#":
            if not end_agents:
                agents.append(soc_line)
            else:
                social.append(parse_social_line(soc_line))
                # convert to agent id
                social[number_of_edges] = (agents.index(social[number_of_edges][0]),agents.index(social[number_of_edges][1]))
                number_of_edges += 1
        else:
            end_agents = True
    return agents, social, number_of_edges

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
    #parse_unsat_pref(model, agents, objects, pref_vars)

def parse_unsat_pref(model, agents, objects, pref_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            for obj2_id in range(len(objects)):
                if pref_vars[agent_id][obj_id][obj2_id] in model:
                    print(f"pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]})")



def decode_clause(clause, agents, objects, alloc_vars):
    result, ids, set_agent, set_obj = parse_better(clause, agents, objects, alloc_vars)
    print(result) if len(result) != 0 else print("False !")
    return ids, set_agent, set_obj 


def parse(model, agents, objects, alloc_vars):
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

def parse_better(model, agents, objects, alloc_vars):
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

def print_at_least_one(agents, objects, set_agent, set_obj):
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
    
def print_not_both(clause,agents, objects,  alloc_vars):
    to_print = "not both "
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in clause:
                to_print += f"alloc_({agents[agent_id]},{objects[obj_id]}) and "
    to_print = to_print[:-5]
    print(to_print) 

def decode_mus(clause_mus, agents, objects, alloc_vars, skip_ones=False):
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
            print_at_least_one(agents, objects, set_agent, set_obj)
        elif len(clause) == 2 and all([lit < 0 for lit in clause]):
            print_not_both(clause, agents, objects,  alloc_vars)
        else:
            if skip_ones and len(clause) == 1:
                one += 1
                continue
            ids_clause, set_agent, set_obj  = decode_clause(clause, agents, objects, alloc_vars)
            set_ag = set_ag.union(set_agent)
            set_ob = set_ob.union(set_obj)
            if ids_clause != None and len(ids_clause) == 2:
                two += 1
            elif ids_clause != None and len(ids_clause) == 1:
                one += 1
            ids.add(ids_clause)
        
    return ids, one, two, set_ag, set_ob

def reduce_MUS(clause_mus, clause2meaning):
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


def draw_other_dag(clause_mus, name, lit_meaning, clause2meaning):
    # TODO

    G = graphviz.Digraph(name)

    at_least_ones = [clause for clause in clause_mus if all((lit>0 for lit in clause))]
    not_boths = [clause for clause in clause_mus if len(clause)==2 and clause[0] < 0 and clause[1] < 0]
    impossibles = [clause for clause in clause_mus if len(clause)==1 and clause[0] < 0]
    chaineds = [clause for clause in clause_mus if not all((lit>0 for lit in clause)) and
                                                   not (len(clause)==2 and clause[0] < 0 and clause[1] < 0) and
                                                   not (len(clause)==1 and clause[0] < 0)]
    


    # first accumulate color    
    colors = ["red3","blue3","yellowgreen","dodgerblue","yellow","green", "violet", "orange", "pink"]
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


def draw_dag(clause_mus, lit_meaning):
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
    

