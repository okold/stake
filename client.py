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
from operator import truediv
from threading import Event, Thread
from tspga import create_tspga
from datetime import datetime as dt
import numpy as np
import pandas
import tsp
import log
import os
 
def create_client(  name = "Client",
                    distance_weight = 0.5, 
                    time_weight = 0.5, 
                    use_other_solution = True,
                    address = ('localhost', 6000),
                    log_path = None,
                    share_result = "best for me"
                    ):

    complete = Event()
    stop_ga = Event()
    stop_ga.set()

    conn_inner, conn_worker = Pipe()
    time_table = None
    

    def pop_string(population):
        s = ""
        for i in range(0,len(population)):
            if i > 0:
                s = s + "\n"
            s = s + str(population[i]) 

        return s

    # Communication / Main Function
    def tsp_client():
        t1 = Thread(target=tsp_worker)
        t1.start()
        
        conn = Client(address)
        conn.send(name)

        # creates an empty log file
        try:
            if log_path != None:
                f = open(log_path, 'w')
                f.write("Name: {}\nDistance Weight: {}\nTime Weight: {}\nUse Other Solution: {}\nResult Strategy: {}\n\n".format(name, distance_weight, time_weight, use_other_solution, share_result))
                f.close()
        except:
            print(dt.now(), name, "could not open log file", log_path)

        current_round = 1
        while complete.is_set() == False:
            if conn.poll():
                cmd = conn.recv()
    
                if cmd[0] == "init":
                    problem = tsp.create_weighted_table(distance_weight, time_weight, cmd[1], cmd[2])
                    log.hr(log_path)
                    log.write(log_path, "R{}".format(current_round), timestamp=True)
                    log.write(log_path, "Received traveling salesman problem.", timestamp=True)
                    conn_inner.send(("init",problem, cmd[3], cmd[4], cmd[5]))

                if cmd == "req_result":
                    log.write(log_path, "Received request for current result. Stopping the GA.", timestamp=True)
                    stop_ga.set()
                    result = conn_inner.recv()
                    conn.send(result)

                if cmd[0] == "continue":
                    current_round += 1
                    log.hr(log_path)
                    log.write(log_path, "R{}".format(current_round), timestamp=True)
                    log.write(log_path, "New population sent by server:".format(current_round), timestamp=True)
                    
                    log.write(log_path, pop_string(cmd[1]))
                    
                    conn_inner.send(("continue", cmd[1]))

                if cmd == "stop":
                    log.write(log_path, "Received stop!", timestamp=True)
                    stop_ga.set()
                    complete.set()
        
        conn.close()
        conn_inner.close()
        t1.join()

    # Worker Function
    def tsp_worker():
        population = distance_table = time_table = chair_weights = None
        problem = None
        count = 1

        while complete.is_set() == False:
            # checks for any commands
            if conn_worker.poll():
                try:
                    cmd = conn_worker.recv()
                    if cmd[0] == "init":
                        problem = cmd[1]
                        distance_table = cmd[2]
                        time_table = cmd[3]
                        chair_weights = cmd[4]
                        stop_ga.clear()

                    if cmd[0] == "continue":
                        if use_other_solution:
                            population = np.vstack((population, cmd[1]))
                            log.write(log_path, "Adding solutions to the pop pool.")
                        else:
                            log.write(log_path, "Rejecting solutions.")
                        stop_ga.clear()
                except:
                    log.write(log_path, "Error in worker thread.")
                    stop_ga.set()
                    complete.set()

            # creates and runs a GA                                 
            if stop_ga.is_set() == False:
                log.write(log_path, "Starting GA {}".format(count), timestamp=True)
                if population is None:
                    log.write(log_path, "Creating initial population.", timestamp=True)
                #else:
                    #log.write(log_path, "Current population:\n{}".format(pop_string(population)))
                instance = create_tspga(    problem,
                                            distance_table,
                                            time_table,
                                            stop_ga = stop_ga, 
                                            population=population,
                                            log_path=log_path)
                instance.run()
                population = instance.population
                sol, _, _ = instance.best_solution()

                if share_result == "best for me":
                    log.write(log_path, "Sending best solution to server:\n{}".format(str(sol)), timestamp=True)
                    conn_worker.send(sol)

                count += 1

        conn_worker.close()

    return Process(target=tsp_client)

def load(   filename = None, 
            pop_multiplier = 1,
            log_dir = None):
    if filename is None:
        filename = "default.csv"

    path = os.path.join("configs", filename)
    config = pandas.read_csv(path)
    config=config.to_numpy()

    client_list = []

    for i in range(0,len(config)):      # for each config
        for j in range(0, pop_multiplier):  # how many duplicates
            name = config[i][0]+ "-" + str(j)

            log_path = None
            if log_dir is not None:
                try:
                    log_path = os.path.join(log_dir, name + ".txt")
                except:
                    log_path = None

            client_list.append(
                create_client(
                    name=name,
                    distance_weight = config[i][1],
                    time_weight = config[i][2],
                    use_other_solution = config[i][3],
                    log_path = log_path
                )
            )

    return client_list
