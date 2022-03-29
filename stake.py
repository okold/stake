################################################################################
# TRAVELING SALESMAN PROBLEM - STAKEHOLDER SEARCH
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
#   ARGUMENTS
# filename:         the name of the file in the problems subdirectory
# config:           the name of the file in the configs subdirectory
# wait_time:        the number of seconds to wait between rounds (default 5)
# num_rounds:       the number of times data is shared among stakeholders
# pop_multiplier:   the number of clients to generate for each configuration
from multiprocessing.connection import Pipe
import tspserver
import pandas
import client
import sys
import tsp
import os

filename = "tsp20.csv"
config = "default.csv"
wait_time = 5
num_rounds = 5
pop_multiplier = 2

if __name__ == "__main__":

    try:
        filename = sys.argv[1]
        config = sys.argv[2]
        wait_time = int(sys.argv[3])
        num_rounds = int(sys.argv[4])
        pop_multiplier = int(sys.argv[5])
    except:
        pass

    print("CURRENT SETTINGS")
    print("filename:      ", filename)
    print("Client config: ", config)
    print("Wait Time:     ", wait_time, "seconds")
    print("Num Rounds:    ", num_rounds)
    print("Pop Multiplier:", pop_multiplier)
    print()

    problem_path = os.path.join("problems", filename)
    
    problem = pandas.read_csv(problem_path, index_col=0)
    client_list = client.load(config, pop_multiplier)
    
    sol_pipe, server_pipe = Pipe()
    server = tspserver.create_server(   problem, 
                                        len(client_list), 
                                        num_rounds=num_rounds, 
                                        wait_time = wait_time,
                                        pipe = server_pipe
                                        )
    server.start()

    for client in client_list:
        client.start()

    server.join()

    for client in client_list:
        client.join()

    best_solution = sol_pipe.recv()
    tsp.plot_solution(problem,best_solution)