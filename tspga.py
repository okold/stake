################################################################################
# TRAVELLING SALESMAN WITH A GENETIC ALGORITHM + AGENT IMPLEMENTATION

import pygad
import numpy as np
import random
import tsp

# PARAMETERS:
# - lookup_table:           the lookup table to use when determining fitness
# - stop_ga:                an Event object to signal an early stop
# - population:             the initial population (default None)
# - parent_selection_type:  PyGAD parent selection type, choices are:
#                           - "rank" (rank selection) DEFAULT
#                           - "sss" (steady-state selection)
#                           - "rws" (roulette wheel selection)
#                           - "sus" (stochastic universal selection)
#                           - "random" (random selection)
#                           - "tournament" (tournament selection)
# - num_parents_mating:     size of parent pool (minimum 2, default 3)     
# - parents_kept:           number of parents kept per generation (default 1)
# - mutation_type:          PyGad mutation type, choices are:
#                           - "inversion" DEFAULT
#                           - "swap"
#                           - "random"
#                           - "scramble"
# - mutation_probability:   PyGad mutation probability (default 0.75)               
def create_tspga(lookup_table, stop_ga, population = None, 
    parent_selection_type = "random", num_parents_mating = 10, parents_kept = 5,
    mutation_type = "scramble", mutation_probability = 0.75):

    N = np.shape(lookup_table)[0]
    POP_SIZE = 200
    NUM_GENS = 10*N

    # returns true if the given list contains duplicates
    # referenced from:
    # https://stackoverflow.com/questions/50883576/fastest-way-to-check-if-duplicates-exist-in-a-python-list-numpy-ndarray
    def contains_duplicates(x):
        return len(np.unique(x)) != len(x)

    # determines the fitness of a solution
    def fitness(solution, solution_idx ):
        return 0 - tsp.total(lookup_table, solution)

    # CROSSOVER FUNCTION
    # gives better results than crossover_type=None
    # ***requires a minimum of two parents!***
    # clones one parent, then picks a second one from the set and swaps one gene
    # as this creates a duplicate gene, continues to swap duplicate genes until all
    # duplicates have been resolved
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

    # prints generation information
    def on_generation(g):
        s, fit, s_i = g.best_solution()

        #if g.generations_completed % 10 == 0:
            #print("GEN", g.generations_completed)
            #print(s)
            #print("Score:\t", tsp.total(lookup_table, s))

        if stop_ga.is_set():
            #g.save(filename="test_save")
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