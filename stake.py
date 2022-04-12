################################################################################
# TRAVELING SALESMAN PROBLEM - STAKEHOLDER SEARCH
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
#   ARGUMENTS
# server_config:    The configuration for the server, as found in the 
#                   server_configs folder, not including the file extension.
#
# num_repeats:      The number of times to run the search.
from multiprocessing.connection import Pipe
from datetime import datetime as dt
from multiprocessing import Process
import tspserver
import pandas
import client
import sys
import tsp
import os

filename = "tsp100.csv"
client_config = "default.csv"
server_config = "20.csv"
wait_time = 60
num_rounds = 60
pop_multiplier = 1
num_top_solutions = 3

if __name__ == "__main__":

    try:
        server_config = sys.argv[1] + ".csv"
    except:
        pass

    server_config = os.path.join("server_configs", server_config)
    server_config = pandas.read_csv(server_config)

    try:
        filename = server_config.at[0, "filename"]
        client_config = server_config.at[0, "client_config"]
        wait_time = int(server_config.at[0, "wait_time"])
        num_rounds = int(server_config.at[0, "num_rounds"])
        pop_multiplier = int(server_config.at[0, "pop_multiplier"])
        num_top_solutions = int(server_config.at[0, "num_top_solutions"])
    except:
        pass

    problem_path = os.path.join("problems", filename)
    log_dir = os.path.join("logs", dt.now().strftime("%Y-%m-%d-%H-%M-%S"))
    os.mkdir(log_dir)
    
    problem = pandas.read_csv(problem_path, index_col=0)

    print("CURRENT SETTINGS")
    print("Filename:      ", filename)
    print("Client config: ", client_config)
    print("Wait Time:     ", wait_time, "seconds")
    print("Num Rounds:    ", num_rounds)
    print("Pop Multiplier:", pop_multiplier)
    print("Num Top Solutions:", num_top_solutions)
    print()

    sol_pipe, server_pipe = Pipe()
        
    client_list = client.load(client_config, pop_multiplier, log_dir=log_dir)

    server = Process(target=tspserver.server_func, 
                    args=[problem, len(client_list)], 
                    kwargs={"pipe": server_pipe, 
                            "wait_time": wait_time, 
                            "num_rounds": num_rounds, 
                            "log_dir": log_dir, 
                            "num_top_solutions": num_top_solutions},
                    daemon=True)
    
    server.start()
    
    for client in client_list:
        client.start()

    server.join()

    for client in client_list:
        client.join()

    best_solution, winner_name = sol_pipe.recv()
    tsp.plot_solution(problem,best_solution,save_path=os.path.join(log_dir, "Solution.png"),name=winner_name)
    sol_pipe.close()
    