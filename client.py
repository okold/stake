################################################################################
# CLIENT
# Parameters
# - name:                   printed by the server
# - distance_weight:        a number between 0 and 1
# - time_weight:            a number between 0 and 1
# - 
# - parent_selection_type:  PyGAD parent selection type, choices are:
#                           - "rank" (rank selection) 
#                           - "sss" (steady-state selection)
#                           - "rws" (roulette wheel selection)
#                           - "sus" (stochastic universal selection)
#                           - "random" (random selection)
#                           - "tournament" (tournament selection)
# - num_parents_mating:     size of parent pool 
# - parents_kept:           number of parents kept per generation
# - mutation_type:          PyGad mutation type, choices are:
#                           - "inversion" 
#                           - "swap"
#                           - "random"
#                           - "scramble"
# - mutation_probability:   PyGad mutation probability (default 0.75)   
from multiprocessing import Process
from multiprocessing.connection import Client, Pipe
from threading import Event, Thread
from tspga import create_tspga

import numpy as np
import pandas
import tsp
import os
 
def create_client(  name = "Client",
                    distance_weight = 1, 
                    time_weight = 0, 
                    use_other_solution = True,
                    address = ('localhost', 6000), 
                    parent_selection_type = "sss", 
                    num_parents_mating = 10, 
                    parents_kept = 5,
                    mutation_type = "scramble", 
                    mutation_probability = 0.75):

    complete = Event()
    stop_ga = Event()
    stop_ga.set()

    conn_inner, conn_worker = Pipe()

    # Communication Function
    def tsp_comm():
        conn = Client(address)
        conn.send(name)
        
        while complete.is_set() == False:
            if conn.poll():
                cmd = conn.recv()
    
                if cmd[0] == "init":
                    problem = tsp.create_weighted_table(distance_weight, time_weight, cmd[1], cmd[2])
                    conn_inner.send(("init",problem))

                if cmd == "req_result":
                    stop_ga.set()
                    result = conn_inner.recv()
                    conn.send(result)

                if cmd[0] == "continue":
                    conn_inner.send(("continue", cmd[1]))

                if cmd == "stop":
                    stop_ga.set()
                    complete.set()
        
        conn.close()
        conn_inner.close()

    # Worker Function
    def tsp_worker():
        population = None
        problem = None
        count = 1

        while complete.is_set() == False:
            if conn_worker.poll():
                cmd = conn_worker.recv()
                if cmd[0] == "init":
                    problem = cmd[1]
                    stop_ga.clear()

                if cmd[0] == "continue":
                    if use_other_solution:
                        population = np.vstack((population, cmd[1]))
                    stop_ga.clear()
                                 
            if stop_ga.is_set() == False:
                instance = create_tspga(problem, stop_ga, 
                    population=population, 
                    parent_selection_type=parent_selection_type,
                    num_parents_mating=num_parents_mating,
                    parents_kept=parents_kept,
                    mutation_type=mutation_type,
                    mutation_probability=mutation_probability)
                instance.run()
                population = instance.population
                s, fit, s_i = instance.best_solution()
                conn_worker.send(s)
                count += 1

        conn_worker.close()

    # Main Process        
    class TSPGA(Process):
        def __init__(self, comm_func, work_func):
            Process.__init__(self, daemon=True)
            self.comm_func = comm_func
            self.work_func = work_func

        def run(self):
            t1 = Thread(target=tsp_worker) # worker function in its own thread
            t1.start()

            tsp_comm()
            t1.join()

    return TSPGA(tsp_comm, tsp_worker)

def load(path = None, pop_multiplier = 1):
    if path == None:
        path = os.path.join("configs", "default.csv")
    
    config = pandas.read_csv(path)
    config=config.to_numpy()

    client_list = []

    for i in range(0,len(config)):      # for each config
        for j in range(0, pop_multiplier):  # how many duplicates
            client_list.append(
                create_client(
                    name=config[i][0]+" - "+str(j),
                    distance_weight=config[i][1],
                    time_weight=config[i][2],
                    use_other_solution=config[i][3]
                )
            )

    return client_list
