################################################################################
# TRAVELING SALESMAN PROBLEM - FRAMEWORK
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
# Functions for generating, loading, evaluating, and plotting a TSP
#
#       generate(N)
# Generates a travelling salesman problem with N points and saves it to a csv 
# file (otherwise, saved to a file named "tspN.csv").
#
#       TSP(path)
# An object which loads a problem from the given path, and provides methods to
# evaluate and plot solutions.
#
#   PARAMETERS
# path: the path to the csv file containing the problem
#   
#   METHODS
# TODO: docs
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

# generates a travelling salesman problem and saves it to a csv file
def generate(N, filename=None):
    coords = []
    for i in range(1,N+1):
        coords.append(str(i) + "," + str(np.random.randint(1,N+1)) + "," + str(np.random.randint(1,N+1)) + "," + str(np.random.uniform(0.5,2.0)))
    
    string = "city,x,y,terrain"
    
    for i in coords:
        string += "\n" + i
    
    if filename is None:
        filename = "tsp" + str(N) + ".csv"

    f = open(filename, "w")
    f.write(string)
    f.close()

class TSP():
    def __init__(self, path):
        self.tsp = pd.read_csv(path, index_col=0)
        (self.distance_table, 
            self.time_table, 
            self.distance_norm, 
            self.time_norm) = self.generate_lookup_tables(self.tsp)
    
    # returns four lookup tables created from the given problem
    # distance_table, time_table, distance_norm, time_norm
    def generate_lookup_tables(self):

        # TODO: replace
        # does this return correctly?
        def distance(a,b):
            return math.sqrt((self.tsp[a,0]-self.tsp[b,0])**2 
                                + (self.tsp[a,1]-self.tsp[b,1])**2)

        def time(a,b):
            return distance(a,b) * self.tsp[a,2] * self.tsp[b,2]
            
        self.tsp = self.tsp.to_numpy()
        length = int(self.tsp.size / 3)
        lookup_table = np.zeros((length, length))
        lookup_table_time = np.zeros((length,length))
        
        for i in range(0,length):
            for j in range(0,length):
                lookup_table[i, j] = lookup_table[j, i] = distance(i,j)
                lookup_table_time[i, j] = lookup_table_time[j, i] = time(i,j)
        
        distance_norm = lookup_table/np.linalg.norm(lookup_table, axis=1)
        time_norm = lookup_table_time/np.linalg.norm(lookup_table_time, axis=1)

        return lookup_table, lookup_table_time, distance_norm, time_norm
    
    def create_weighted_table(self, distance_weight = 0.5, time_weight = 0.5):
        dist_norm = self.distance_table*distance_weight
        time_norm = self.time_table*time_weight
        return dist_norm+time_norm

    # returns the total distance of a given solution
    def total(self, sol, lookup_table = None):
        if lookup_table is None:
            lookup_table = self.distance_table

        N = len(sol)-1
        total = 0

        for i in range(0,N):
            total += lookup_table[sol[i]-1, sol[i+1]-1]
        total += lookup_table[sol[N]-1, sol[0]-1]
        return total
    
    # determines the fitness of a solution
    def fitness(self, solution, lookup_table = None):
        if lookup_table is None:
            lookup_table = self.distance_table

        return 0 - total(lookup_table, solution)

# loads a TSP from a given file
def load(filename):
    return pd.read_csv(filename, index_col=0)

# plots a given solution
def plot_solution(tsp, solution, save_path = None, name = None):
    x = []
    y = []
    for i in range(0,len(solution)):
        x.append(tsp.loc[solution[i]][0])
        y.append(tsp.loc[solution[i]][1])
    
    x.append(tsp.loc[solution[0]][0])
    y.append(tsp.loc[solution[0]][1])

    for i in range(0,len(x)-1):
        plt.xlabel("Position (x)")

        terrain = tsp.loc[solution[i]][2]

        if terrain < 1:
            plt.plot(x[i], y[i], marker="o", color="green")
        else:
            if terrain > 1.5:
                plt.plot(x[i], y[i], marker="o", color="red")
            else:
                plt.plot(x[i], y[i], marker="o", color="blue")
        if name is not None:
            plt.suptitle(name)

        plt.arrow(  x[i], 
                    y[i], 
                    (x[i+1] - x[i]), 
                    (y[i+1] - y[i]),
                    length_includes_head=True
                    )

    if save_path is not None:
        plt.savefig(save_path)

    plt.show()

# returns four lookup tables created from the given problem
# distance_table, time_table, distance_norm, time_norm
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

# weighs two tables together
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
    return 1 / total(lookup_table, solution)