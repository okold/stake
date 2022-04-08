################################################################################
# TRAVELING SALESMAN PROBLEM - SERVER
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
#       create_server(problem, num_clients)
# Returns a Process which acts as a server for a stakeholder search approach
# to the traveling salesman problem.
#
#   PARAMETERS
# problem:          a pandas dataframe containing the problem data
# num_clients:      the number of clients (stakeholders) to work on the problem
#
#   OPTIONAL PARAMETERS
# wait_time:        the number of seconds to wait between rounds (default 5)
# num_rounds:       the number of rounds to run the algorithm (default 5)
# distance_weight:  the weight to apply to fitness using distance (default 0.5)
# time_weight:      the weight to apply to fitness using time (default 0.5)
# address:          the server's address (default ("localhost", 6000))
# pipe:             a Connection object to send the best solution to main
from datetime import datetime
from multiprocessing import Process
from multiprocessing.connection import Listener
import numpy as np
import time
import log
import os
import tsp

# holds data for a single client
class Stakeholder():
    def __init__(self, conn, name, distance_table, time_table):
        self.name = name
        self.conn = conn
        self.last_result = None
        self.distance_table = distance_table
        self.time_table = time_table

    def try_recv(self):
        try:
            if self.conn.poll():
                self.last_result = self.conn.recv()
                return True
        except EOFError:
            pass

        return False

    def __str__(self):
        s = "{} {:>22} D: {:.2f} T: {:.2f} {}".format(datetime.now(), 
                                            self.name, 
                                            tsp.total(self.distance_table, self.last_result), 
                                            tsp.total(self.time_table, self.last_result), 
                                            self.last_result)
        return s

# a collection of stakeholders
class Committee():
    def __init__(self, distance_table, time_table):
        self.stakeholder_list = []
        self.max_name_length = 0
        self.top = []
        self.distance_table = distance_table
        self.time_table = time_table

    # adds a stakeholder to the committee
    def add(self, conn, name):
        self.stakeholder_list.append(Stakeholder(conn, name, self.distance_table, self.time_table))
        self.max_name_length = max(self.max_name_length, len(name))

    # sends the same message to all clients
    def send_to_all(self, message):
        for s in self.stakeholder_list:
            s.conn.send(message)

    # requests data from all clients, then waits to receive it 
    def recv_from_all(self):
        self.send_to_all("req_result")

        waiting_list = []
        for stakeholder in self.stakeholder_list:
            waiting_list.append(stakeholder)

        while waiting_list != []:
            for stakeholder in waiting_list:
                if stakeholder.try_recv():  # if you successfully get data
                    waiting_list.remove(stakeholder)

    # closes all connections
    def close_all(self):
        for s in self.stakeholder_list:
            s.conn.close()

    # returns a numpy array containing the best solution using the given lookup table
    def get_best_solution(self, lookup_table):
        if self.top == []:
            self.find_top_solutions(lookup_table)
        
        return self.top[0]

    # returns the top N unique solutions, default 3
    # DOES NOT RETURN THE STAKEHOLDERS THEMSELVES
    def find_top_solutions(self, lookup_table, N = 3):
        top = []
        for stakeholder in self.stakeholder_list:

            no_duplicates = True
            for i in range(0,len(top)):
                if np.array2string(stakeholder.last_result) == np.array2string(top[i].last_result):
                    no_duplicates = False

            if no_duplicates:
                if len(top) < N:
                    top.append(stakeholder)
                else:
                    if tsp.total(lookup_table, stakeholder.last_result) < tsp.total(lookup_table, top[N-1].last_result):
                        top.remove(top[N-1])
                        top.append(stakeholder)
            top.sort(key=lambda x: tsp.total(lookup_table, x.last_result))
        self.top = top    
        return list(map(lambda x: x.last_result, top)) 
    
    # prints all solutions
    def print_all(self):
        for s in self.stakeholder_list:
            print(s)

    # prints the top solution
    def print_top(self, best=False):
        if best:
            print(self.top[0])
        else:
            for s in self.top:
                print(s)

    def csv_header(self):
        header = ["Round", "Time", "Best Solution Stakeholder", "Best Solution Fitness"]
        for s in self.stakeholder_list:
            header.append(s.name)
        return header

    def csv_solutions(self, round, table):
        arr = [str(round), str(datetime.now())]
        arr.append(self.top[0].name)
        arr.append(str(tsp.fitness(table, self.top[0].last_result)))
        for s in self.stakeholder_list:
            arr.append(str(tsp.fitness(table, s.last_result)))
        return arr

def server_func(problem,
                num_clients, 
                wait_time=5,
                num_rounds = 5, 
                pipe = None, 
                distance_weight = 0.5, 
                time_weight = 0.5, 
                address = ("localhost", 6000),
                log_dir = None):

    csv_path = os.path.join(log_dir, "Server.csv")
    csv = log.CSVLogFile(csv_path)

    distance_table, time_table, distance_norm, time_norm = tsp.create_lookup_tables(problem)
    chair_weights = tsp.create_weighted_table(distance_weight, time_weight, distance_norm, time_norm)

    start_time = datetime.now()
    listener = Listener(address)
    c = Committee(distance_table, time_table)

    try:
        # connects to all clients
        for i in range(0, num_clients):
            conn = listener.accept()
            name = conn.recv()
            c.add(conn, name)
    except:
        listener.close()

    csv.write(c.csv_header())

    # rounds
    top_solutions = []

    for i in range(0, num_rounds):
        print()
        print(datetime.now(), "BEGINNING ROUND", i+1)

        # sends command/data to all clients
        if i == 0:
            c.send_to_all(("init", distance_norm, time_norm, distance_table, time_table, chair_weights))
        else:
            c.send_to_all(("continue", top_solutions))

        time.sleep(wait_time)

        # receives data from all clients
        print(datetime.now(), "Receiving results...")
        c.recv_from_all()
        c.print_all()

        # records and prints the top solutions
        print()
        print(datetime.now(), "Top solutions for round", i+1)
        top_solutions = c.find_top_solutions(chair_weights)
        c.print_top()
        csv.write(c.csv_solutions(i+1, chair_weights))
    
    # sends stop command to all clients
    c.send_to_all(("stop"))
    print()
    print(datetime.now(), "Sent stop!")

    # prints the best solution
    print()
    print(datetime.now(), "Best solution found:")
    c.print_top(best=True)

    total_time = (datetime.now() - start_time).total_seconds()
    print(datetime.now(), "Total Time: {} seconds (expected {})".format(total_time, num_rounds * wait_time))

    # sends the best solution for drawing
    if pipe != None:
        stakeholder = c.get_best_solution(chair_weights)
        pipe.send((stakeholder.last_result, "{} | D: {:.2f} | T: {:.2f} | F: {:.2f}".format(stakeholder.name, tsp.total(distance_table, stakeholder.last_result), tsp.total(time_table, stakeholder.last_result), tsp.fitness(chair_weights, stakeholder.last_result))))
        #pipe.close()

    #c.close_all()