import numpy as np
import matplotlib.pyplot as plt
import math

# plots a given solution
# referenced:
# https://gist.github.com/payoung/6087046
def plot_solution(tsp, solution):
    x = []
    y = []
    for i in range(0,len(solution)):
        x.append(tsp.loc[solution[i]][0])
        y.append(tsp.loc[solution[i]][1])
    
    x.append(tsp.loc[solution[0]][0])
    y.append(tsp.loc[solution[0]][1])

    #plt.plot(x, y, "co")

    for i in range(0,len(x)-1):
        plt.arrow(x[i], y[i], 
        (x[i+1] - x[i]), (y[i+1] - y[i]),
        length_includes_head=True)
    
    plt.show()

# returns normalized lookup tables created from the given tsp
# distance_table, time_table
def create_lookup_tables(tsp):

    # does this return correctly?
    def distance(a,b):
        return math.sqrt((tsp[a,0]-tsp[b,0])**2 + (tsp[a,1]-tsp[b,1])**2)

    def time(a,b):
        return distance(a,b) * tsp[a,2] * tsp[b,2]
        
    tsp = tsp.to_numpy()
    length = int(tsp.size / 3)
    lookup_table = np.zeros((length, length))
    lookup_table_time = np.zeros((length,length))
    
    for i in range(0,length):
        for j in range(0,length):
            lookup_table[i, j] = lookup_table[j, i] = distance(i,j)
            lookup_table_time[i, j] = lookup_table_time[j, i] = time(i,j)
    
    distance_norm = lookup_table/np.linalg.norm(lookup_table, axis=1)
    time_norm = lookup_table_time/np.linalg.norm(lookup_table_time, axis=1)

    return lookup_table, lookup_table_time, distance_norm, time_norm

# weighs the two tables together
def create_weighted_table(distance_weight, time_weight, distance_table, time_table):
    dist_norm = distance_table*distance_weight
    time_norm = time_table*time_weight
    return dist_norm+time_norm

# returns the total distance of a given solution
def total(lookup_table, sol):
    N = len(sol)-1
    total = 0

    for i in range(0,N):
        total += lookup_table[sol[i]-1, sol[i+1]-1] #indices starting at 1 smh
    total += lookup_table[sol[N]-1, sol[0]-1]
    return total

# determines the fitness of a solution
def fitness(lookup_table,solution):
    return 0 - total(lookup_table, solution)

# distance
def best_solution(lookup_table, solution_list):
    best_solution = solution_list[0]

    for solution in solution_list:
            if total(lookup_table, solution) < total(lookup_table, best_solution):
                best_solution = solution

    return best_solution

