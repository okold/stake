################################################################################
# TRAVELING SALESMAN PROBLEM - FRAMEWORK
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
# Functions for generating, loading, evaluating, and plotting a TSP
#
# The expected format of a TSP is a csv file with the following columns:
#   city,x,y,terrain
# where city is the name of the city, x and y are the coordinates, and terrain
# is a "cost" value for travelling to that city, for calculating time.
#
# Time is calculated by multiplying the distance between two points by both of
# their "terrain" costs.
#
# FUNCTIONS
#
#       generate(N)
# Generates a travelling salesman problem with N points and saves it to a csv 
# file (otherwise, saved to a file named "tspN.csv").
#
#       load(filename)
# Loads a TSP from a given file, returning a pandas dataframe.
#
#       create_lookup_tables(tsp)
# Creates four lookup tables from a given TSP, returning them as a tuple. The
# return values are:
#   distance_table: a table of distances between each pair of cities
#   time_table: a table of times between each pair of cities
#   distance_norm: a table of normalized distances between each pair of cities
#   time_norm: a table of normalized times between each pair of cities
#
#       create_weighted_table(distance_weight, time_weight, distance_table, time_table)
# Creates a single table using the given weights and lookup tables.
#
#       total(lookup_table, solution)
# Totals the cost of a solution, given a lookup table.
#
#       fitness(lookup_table, solution)
# Returns the fitness of a solution, given a lookup table.
#
#       best(population, lookup_table)
# Returns the best solution in a population.
#
#       plot_solution(tsp, solution, save_path = None, name = None)
# Plots and shows a solution using matplotlib.
#
#       pop_string(population)
# Returns a string representation of a population, for debugging/logging.
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

# loads a TSP from a given file
def load(filename):
    return pd.read_csv(filename, index_col=0)

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

# creates a single table out of the given weights and lookup tables
def create_weighted_table(distance_weight, time_weight, distance_table, time_table):
    dist_norm = distance_table*distance_weight
    time_norm = time_table*time_weight
    return dist_norm+time_norm

# returns the total distance of a given solution
def total(lookup_table, sol):
    N = len(sol)-1
    total = 0

    for i in range(0,N):
        total += lookup_table[sol[i]-1, sol[i+1]-1]
    total += lookup_table[sol[N]-1, sol[0]-1]
    return total

# determines the fitness of a solution
def fitness(lookup_table,solution):
    return 1 / total(lookup_table, solution)

# returns the best solution in a population
def best(population, lookup_table):
    best = population[0]
    for i in range(1,len(population)):
        if fitness(lookup_table, population[i]) > fitness(lookup_table, best):
            best = population[i]
    return best

# plots a given solution
def plot_solution(tsp, solution, save_path = None, name = None):

    plt.rcParams['figure.figsize'] = [8, 8]

    x = []
    y = []
    for i in range(0,len(solution)):
        x.append(tsp.loc[solution[i]][0])
        y.append(tsp.loc[solution[i]][1])
    
    x.append(tsp.loc[solution[0]][0])
    y.append(tsp.loc[solution[0]][1])
    plt.ylabel("Position (y)")
    plt.xlabel("Position (x)")

    green = None
    blue = None
    red = None

    for i in range(0,len(x)-1):
        terrain = tsp.loc[solution[i]][2]

        if terrain < 1:
            green = plt.plot(x[i], y[i], marker="o", color="green")
        else:
            if terrain > 1.5:
                red = plt.plot(x[i], y[i], marker="o", color="red")
            else:
                blue = plt.plot(x[i], y[i], marker="o", color="blue")
        if name is not None:
            plt.suptitle(name)

        plt.arrow(  x[i], 
                    y[i], 
                    (x[i+1] - x[i]), 
                    (y[i+1] - y[i]),
                    length_includes_head=True
                    )

    plt.legend(
        title="Time Cost (t)",
        handles=[green[0], blue[0], red[0]],
        labels=["t < 1.0", "1.0 <= t <= 1.5", "1.5 < t"]
        )

    if save_path is not None:
        plt.savefig(save_path)

    plt.show()

# prints out a population
def pop_string(population):
    s = ""
    for i in range(0,len(population)):
        if i > 0:
            s = s + "\n"
        s = s + str(population[i]) 

    return s
