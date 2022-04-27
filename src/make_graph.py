from time import time
import matplotlib.pyplot as plt

if __name__ == "__main__":
    dossier = "C:/Users/killi/Documents/new_PB_LEF/PB_LEF/src/graphique/"
    total_times = dict()
    construct_times = dict()
    solving_times = dict()
    timeout = dict()
    LEF_instances = dict()

    avg_total_time = dict()
    avg_construct_time = dict()
    avg_solving_time = dict()

    
    num_agents = [10,20,30,40,50,75,100]
    probs = [0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.75,0.9]
    lef_formulas = ["pairs", "complement", "consequence"]

    for prob in probs:
        for num_agent in num_agents:
            LEF_instances[(num_agent, prob)] = 0

    for lef_formula in lef_formulas:
        for prob in probs:
            for ha in ["both"]:
                for num_agent in num_agents:
                    total_times[(num_agent, prob, ha, lef_formula)] = []
                    construct_times[(num_agent, prob, ha, lef_formula)] = []
                    solving_times[(num_agent, prob, ha, lef_formula)] = []
                    timeout[(num_agent, prob, ha, lef_formula)] = 0
                    path_name = f"{dossier}inst_{ha}_{num_agent}_{prob}_{lef_formula}.txt"
                    with open(file=path_name, mode='r') as f:
                        for line in f.readlines():
                            splited_line = line.split()
                            if splited_line[0] == "timeout!":
                                #if prob==0.2 and num_agent==100:
                                #    print(f"{lef_formula:13} timeout")
                                total_times[(num_agent, prob, ha, lef_formula)].append(150.0)
                                construct_times[(num_agent, prob, ha, lef_formula)].append(-1.0)
                                solving_times[(num_agent, prob, ha, lef_formula)].append(150.0)
                                timeout[(num_agent, prob, ha, lef_formula)] += 1
                            else:
                                #if prob==0.2 and num_agent==100:
                                #    print(f"{lef_formula:13} {float(splited_line[2]):6.3f} {splited_line[3]}")
                                total_times[(num_agent, prob, ha, lef_formula)].append(float(splited_line[0]))
                                construct_times[(num_agent, prob, ha, lef_formula)].append(float(splited_line[1]))
                                solving_times[(num_agent, prob, ha, lef_formula)].append(float(splited_line[2]))
                                if lef_formula == "pairs":
                                    LEF_instances[(num_agent, prob)] += 1 if splited_line[3] == "False" else 0

                    # a bit of hacking (didn't record the construct time for timed-out instances)
                    trimmed_construct = [t for t in construct_times[(num_agent, prob, ha, lef_formula)] if t >= 0.0]

                    avg_construct_time[(num_agent, prob, ha, lef_formula)] =  (sum(trimmed_construct) / len(trimmed_construct))
                    construct_times[(num_agent, prob, ha, lef_formula)] = [t if t >= 0.0 else avg_construct_time[(num_agent, prob, ha, lef_formula)] for t in construct_times[(num_agent, prob, ha, lef_formula)] ]
                    avg_solving_time[(num_agent, prob, ha, lef_formula)] = sum(solving_times[(num_agent, prob, ha, lef_formula)]) / len(solving_times[(num_agent, prob, ha, lef_formula)])
                    avg_total_time[(num_agent, prob, ha, lef_formula)] = avg_construct_time[(num_agent, prob, ha, lef_formula)] + avg_solving_time[(num_agent, prob, ha, lef_formula)]
                    
                    avg_construct =avg_construct_time[(num_agent, prob, ha, lef_formula)]
                    avg_solving = avg_solving_time[(num_agent, prob, ha, lef_formula)]
                    avg_total = avg_total_time[(num_agent, prob, ha, lef_formula)] 
                    
                    total_times[(num_agent, prob, ha, lef_formula)] = [t if t>=0.0 else avg_construct for t in total_times[(num_agent, prob, ha, lef_formula)] ]
                    
                    #print(f"{lef_formula:13} {num_agent:3} {ha:7} {prob:4} : {avg_total:10f} {avg_construct:10f} {avg_solving:10f} {timeout[(num_agent, prob, ha, lef_formula)]:2}")

    # print(f"{probs}")
    # for lef_formula in lef_formulas:
    #     for num_agent in num_agents:

    #         to_print = ""
    #         for prob in probs:
    #             to_print += f"{avg_solving_time[(num_agent, prob, 'both', lef_formula)]} "
    #         print(to_print)


    # for prob in probs:
    #     for num_agent in num_agents:
    #         print(f"{num_agent:3} {prob:4} : {LEF_instances[(num_agent, prob)]}")

    # plt.figure(figsize=(10,7))
    # plt.plot(list(range(1,21)), solving_times[(100, 0.285, "both", "pairs")],'bo', label=f"pairs {avg_solving_time[(num_agent, prob, 'both', 'pairs')]}")
    # plt.plot(list(range(1,21)), solving_times[(100, 0.285, "both", "special")], 'ro', label=f"pairs+consequence {avg_solving_time[(num_agent, prob, 'both', 'special')]}")


    # plt.xlabel('instance #')
    # plt.ylabel('time (sec)')
    # plt.legend()
    # plt.title(f"pairs vs pairs+consequence formulations (n=100,p=0.285)")
    # plt.savefig(f"solving_compare.jpg")
    
    for lef_formula in lef_formulas:
    #     plt.figure(figsize=(10,7))
    #     plt.plot(num_agents, [[avg_total_time[(num_agent, prob, "both", f"{lef_formula}")] for prob in probs]for num_agent in num_agents])
    #     plt.xlabel('Number of agents')
    #     plt.ylabel('average time (sec)')
    #     plt.legend([prob for prob in probs])
    #     plt.title(f"\"{lef_formula}\" formulation")
    #     plt.savefig(f"{lef_formula}_total_agents.jpg")

    #     plt.figure(figsize=(10,7))
    #     plt.plot(num_agents, [[avg_construct_time[(num_agent, prob, "both", f"{lef_formula}")] for prob in probs]for num_agent in num_agents])
    #     plt.xlabel('Number of agents')
    #     plt.ylabel('average time (sec)')
    #     plt.legend([prob for prob in probs])
    #     plt.title(f"\"{lef_formula}\" formulation")
    #     plt.savefig(f"{lef_formula}_construct_agents.jpg")

    #     plt.figure(figsize=(10,7))
    #     plt.plot(num_agents, [[avg_solving_time[(num_agent, prob, "both", f"{lef_formula}")] for prob in probs]for num_agent in num_agents])
    #     plt.xlabel('Number of agents')
    #     plt.ylabel('average time (sec)')
    #     plt.legend([prob for prob in probs])
    #     plt.title(f"\"{lef_formula}\" formulation")
    #     plt.savefig(f"{lef_formula}_solving_agents.jpg")


        plt.figure(figsize=(10,7))
        plt.plot(probs, [[avg_total_time[(num_agent, prob, "both", f"{lef_formula}")] for num_agent in num_agents]for prob in probs])
        plt.xlabel('Erdos-Renyi social network (probability parameter)')
        plt.ylabel('average time (sec)')
        plt.legend([num_agent for num_agent in num_agents])
        plt.title(f"\"{lef_formula}\" formulation")
        plt.savefig(f"{lef_formula}_total_probs_new.jpg")

        plt.figure(figsize=(10,7))
        plt.plot(probs, [[avg_construct_time[(num_agent, prob, "both", f"{lef_formula}")] for num_agent in num_agents]for prob in probs])
        plt.xlabel('Erdos-Renyi social network (probability parameter)')
        plt.ylabel('average time (sec)')
        plt.legend([num_agent for num_agent in num_agents])
        plt.title(f"\"{lef_formula}\" formulation")
        plt.savefig(f"{lef_formula}_construct_probs_new.jpg")

        plt.figure(figsize=(10,7))
        plt.plot(probs, [[avg_solving_time[(num_agent, prob, "both", f"{lef_formula}")]  for num_agent in num_agents]for prob in probs])
        plt.xlabel('Erdos-Renyi social network (probability parameter)')
        plt.ylabel('average time (sec)')
        plt.legend([num_agent for num_agent in num_agents])
        plt.title(f"\"{lef_formula}\" formulation")
        plt.savefig(f"{lef_formula}_solving_probs_new.jpg")
