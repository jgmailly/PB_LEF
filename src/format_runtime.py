import matplotlib.pyplot as plt

##### À exécuter après make_stats.sh


def avg_list(l):
    sum_list = 0
    for elem in l:
        sum_list += elem
    return sum_list/len(l)

def get_list_from_file(filename):
    result = []
    f = open(filename, "r")
    for line in f:
        result.append(float(line))
    f.close()
    return result

x_values = [10,20,30,40,50]

## Erdos-Renyi instances
# prefix = "RESULTS_ER_0.0/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.0")

# prefix = "RESULTS_ER_0.1/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.1")

# prefix = "RESULTS_ER_0.3/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.3")

# prefix = "RESULTS_ER_0.5/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.5")

# prefix = "RESULTS_ER_0.7/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.7")

# prefix = "RESULTS_ER_0.9/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=0.9")

# prefix = "RESULTS_ER_1.0/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="p=1.0")

# plt.xlabel("Number of agents")
# plt.ylabel("Average runtime (s)")
# plt.legend()
# #plt.show()
# plt.savefig("results-runtime-ER.png")

## Path instances
# prefix = "RESULTS_PATH/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values) #, label="p=1.0")

# ## BA instances
# prefix = "RESULTS_BA_1/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=1")

# prefix = "RESULTS_BA_2/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2")

# prefix = "RESULTS_BA_3/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=3")

# prefix = "RESULTS_BA_4/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4")

# prefix = "RESULTS_BA_5/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=5")

## WS Instances
# prefix = "RESULTS_WS_2_0.1/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2, p=0.1")


# prefix = "RESULTS_WS_2_0.3/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2, p=0.3")

# prefix = "RESULTS_WS_2_0.5/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2, p=0.5")

# prefix = "RESULTS_WS_2_0.7/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2, p=0.7")

# prefix = "RESULTS_WS_2_0.9/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=2, p=0.9")

# prefix = "RESULTS_WS_4_0.1/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4, p=0.1")


# prefix = "RESULTS_WS_4_0.3/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4, p=0.3")

# prefix = "RESULTS_WS_4_0.5/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4, p=0.5")

# prefix = "RESULTS_WS_4_0.7/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4, p=0.7")

# prefix = "RESULTS_WS_4_0.9/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=4, p=0.9")

# prefix = "RESULTS_WS_6_0.1/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=6, p=0.1")


# prefix = "RESULTS_WS_6_0.3/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=6, p=0.3")

# prefix = "RESULTS_WS_6_0.5/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=6, p=0.5")

# prefix = "RESULTS_WS_6_0.7/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=6, p=0.7")

# prefix = "RESULTS_WS_6_0.9/"
# files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
# y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
# plt.plot(x_values,y_values, label="m=6, p=0.9")

prefix = "RESULTS_WS_8_0.1/"
files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
plt.plot(x_values,y_values, label="m=8, p=0.1")


prefix = "RESULTS_WS_8_0.3/"
files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
plt.plot(x_values,y_values, label="m=8, p=0.3")

prefix = "RESULTS_WS_8_0.5/"
files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
plt.plot(x_values,y_values, label="m=8, p=0.5")

prefix = "RESULTS_WS_8_0.7/"
files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
plt.plot(x_values,y_values, label="m=8, p=0.7")

prefix = "RESULTS_WS_8_0.9/"
files = [f"{prefix}results_10.time",f"{prefix}results_20.time",f"{prefix}results_30.time",f"{prefix}results_40.time",f"{prefix}results_50.time"]
y_values = [avg_list(get_list_from_file(files[i])) for i in range(len(files))]
plt.plot(x_values,y_values, label="m=8, p=0.9")

plt.xlabel("Number of agents")
plt.ylabel("Average runtime (s)")
plt.legend()
#plt.show()
plt.savefig("results-runtime-WS-8.png")
