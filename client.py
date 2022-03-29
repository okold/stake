################################################################################
# TRAVELING SALESMAN PROBLEM - CLIENT (GENETIC ALGORITHM)
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
#       create_client()
# Returns a TSPGA object, which is a subclass of Process. Upon running the
# process, it will attempt to connect to the server at the specified address,
# and participate in a number of rounds as a stakeholder.
#
#   OPTIONAL PARAMETERS
# name:               - name of the client as printed by the server, otherwise 
#                       a generated one is used
# distance_weight:    - weight of distance in the fitness function (default 0.5)
# time_weight:        - weight of time in the fitness function (default 0.5)
# use_other_solution: - whether to include the solutions shared by the chair in 
#                       the next round of search (default True)
# address:            - the address of the server (default ('localhost', 6000))
#
#       load()
# Returns a list of TSPGA objects, as determined by the given config file.
#
#   OPTIONAL PARAMETERS
# filename:           - name of the config file (default "default.csv")
# pop_multiplier:     - how many times to duplicate each config (default 1)
from multiprocessing.connection import Client, Pipe
from multiprocessing import Process
from threading import Event, Thread
from tspga import create_tspga
import numpy as np
import pandas
import tsp
import os
 
def create_client(  name = "Client",
                    distance_weight = 0.5, 
                    time_weight = 0.5, 
                    use_other_solution = True,
                    address = ('localhost', 6000)
                    ):

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
                instance = create_tspga(problem, stop_ga, population=population)
                instance.run()
                population = instance.population
                sol, _, _ = instance.best_solution()
                conn_worker.send(sol)
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

def load(filename = None, pop_multiplier = 1):
    if filename is None:
        filename = "default.csv"

    path = os.path.join("configs", filename)
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
