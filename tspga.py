################################################################################
# TRAVELING SALESMAN PROBLEM - GENETIC ALGORITHM
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
#       create_tspga(lookup_table, distance_table, time_table, stop_ga, 
#                       population, parent_selection_type, parents_kept, 
#                       mutation_type, mutation_probability, log_path)
# Returns a PyGAD instance for the traveling salesman problem.
#
#   PARAMETERS
# lookup_table:             the lookup table to use when determining fitness
#
#   OPTIONAL PARAMETERS
# stop_ga:                  an Event object to signal an early stop
# population:               the initial population (default None)
# parent_selection_type:    PyGAD parent selection type, choices are:
#                           - "rank" (rank selection) DEFAULT
#                           - "sss" (steady-state selection)
#                           - "rws" (roulette wheel selection)
#                           - "sus" (stochastic universal selection)
#                           - "random" (random selection)
#                           - "tournament" (tournament selection)
# num_parents_mating:       size of the parent pool (minimum 2, default 3)     
# parents_kept:             number of parents kept per generation (default 1)
# mutation_type:            PyGad mutation type, choices are:
#                           - "inversion" DEFAULT
#                           - "swap"
#                           - "random"
#                           - "scramble"
# mutation_probability:     - PyGad mutation probability (default 0.75)
# log_path:                 - path to the log file (default None)      
import datetime as dt
import numpy as np
import pygad
import random
import tsp
import log
           
def create_tspga(   lookup_table,
                    distance_table,
                    time_table,
                    stop_ga = None, 
                    population = None, 
                    parent_selection_type = "sss", 
                    parents_kept = 5,
                    mutation_type = "inversion", 
                    mutation_probability = 0.75,
                    log_path = None
                    ):

                    
    N = np.shape(lookup_table)[0]
    num_parents_mating = int(N/2) 
    POP_SIZE = 200
    NUM_GENS = 10*N

    if num_parents_mating < 2:
        num_parents_mating = 2

    if parents_kept > num_parents_mating:
        parents_kept = num_parents_mating

    # returns true if the given list contains duplicates
    # referenced from:
    # https://stackoverflow.com/questions/50883576/fastest-way-to-check-if-duplicates-exist-in-a-python-list-numpy-ndarray
    def contains_duplicates(x):
        return len(np.unique(x)) != len(x)

    # determines the fitness of a solution
    def fitness(solution, solution_idx ):
        return tsp.fitness(lookup_table, solution)

    # CROSSOVER FUNCTION
    # gives better results than crossover_type=None
    # ***requires a minimum of two parents!***
    # clones one parent, then picks a second one from the set and swaps one gene
    # as this creates a duplicate gene, continues to swap duplicate genes until 
    # all duplicates have been resolved
    def cascade_crossover(parents, offspring_size, ga_instance):
        offspring = []
        N = len(parents) - 1
        while len(offspring) != offspring_size[0]:
            p1 = random.randint(0,N) #index of parent 1
            p2 = random.randint(0,N) #index of parent 2

            while p2 == p1:
                p2 = random.randint(0,N)

            child = parents[p1].copy()

            swap_index = random.randint(0,N)
            child[swap_index] = parents[p2][swap_index]

            # if the swap creates a duplicate gene,
            # continues to swap genes until all duplicates have been eliminated
            while (contains_duplicates(child)):
                swap_index = np.where(parents[p1]==child[swap_index])
                child[swap_index] = parents[p2][swap_index]

            offspring.append(child)
        return np.array(offspring)

    # logs generation information
    def on_generation(g):
        s, fit, _ = g.best_solution()
        
        log.write(log_path, "GEN {:02d} - Distance: {:.8} - Time: {:.8}\n{}".format(g.generations_completed, tsp.total(distance_table, s), tsp.total(time_table, s), s), timestamp=True)

        if stop_ga != None and stop_ga.is_set():
            return "stop"

    ga_instance = pygad.GA(
        initial_population=population,

        num_generations=NUM_GENS,                  
        fitness_func=fitness,
        on_generation=on_generation,
        sol_per_pop=POP_SIZE,
        num_genes=N,

        allow_duplicate_genes=False,            
        gene_space = range(1, N+1),
        gene_type=int,
        mutation_type=mutation_type,              
        mutation_probability=mutation_probability,        
                                                
        num_parents_mating=num_parents_mating,                   
        parent_selection_type=parent_selection_type,
        crossover_type=cascade_crossover,
        keep_parents=parents_kept
    )
    return ga_instance