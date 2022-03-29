import sys
import pandas
from multiprocessing.connection import Pipe
import tsp
import client
from server import create_server
import os

FILENAME = "tsp20.csv"
CONFIG = "default.csv"
WAIT_TIME = 5
NUM_ROUNDS = 5
POP_MULTIPLIER = 2

if __name__ == "__main__":

    try:
        FILENAME = sys.argv[1]
        CONFIG = sys.argv[2]
        WAIT_TIME = int(sys.argv[3])
        NUM_ROUNDS = int(sys.argv[4])
    except:
        pass

    problem_path = os.path.join("problems", FILENAME)
    config_path = os.path.join("configs", CONFIG)
    
    problem = pandas.read_csv(problem_path, index_col=0)
    client_list = client.load(config_path, POP_MULTIPLIER)
    
    sol_pipe, server_pipe = Pipe()



    server = create_server(problem, server_pipe, WAIT_TIME, len(client_list), num_rounds=NUM_ROUNDS)

    server.start()

    for client in client_list:
        client.start()

    server.join()

    for client in client_list:
        client.join()

    best_solution = sol_pipe.recv()
    tsp.plot_solution(problem,best_solution)