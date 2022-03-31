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
import tsp
    
def create_server(  problem,
                    num_clients, 
                    wait_time=5,
                    num_rounds = 5, 
                    pipe = None, 
                    distance_weight = 0.5, 
                    time_weight = 0.5, 
                    address = ("localhost", 6000)
                    ):

    # a collection of stakeholders
    class Committee():
        def __init__(self, distance_table, time_table):
            self.stakeholder_list = []
            self.max_name_length = 0
            self.top = []
            self.distance_table = distance_table
            self.time_table = time_table
        
        # holds data for a single client
        class Stakeholder():
            def __init__(self, conn, name):
                self.name = name
                self.conn = conn
                self.last_result = None

            def try_recv(self):
                try:
                    if self.conn.poll():
                        self.last_result = self.conn.recv()
                        return True
                except EOFError:
                    pass

                return False
            
            def print_solution(self, max_length, distance_table, time_table):
                name = "{:>" + str(max_length) + "}"
                print(  datetime.now(), 
                        name.format(self.name), 
                        self.last_result, 
                        "D: {:.2f}".format(tsp.total(distance_table, self.last_result)),
                        "T: {:.2f}".format(tsp.total(time_table, self.last_result))
                )

        # adds a stakeholder to the committee
        def add(self, conn, name):
            self.stakeholder_list.append(self.Stakeholder(conn, name))
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
            
            return self.top[0].last_result, self.top[0].name

        # returns the top N unique solutions, default 3
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
                s.print_solution(self.max_name_length, self.distance_table, self.time_table)

        # prints the top solution
        def print_top(self, best=False):
            if best:
                self.top[0].print_solution(self.max_name_length, self.distance_table, self.time_table)
            else:
                for s in self.top:
                    s.print_solution(self.max_name_length, self.distance_table, self.time_table)

    distance_table, time_table, distance_norm, time_norm = tsp.create_lookup_tables(problem)
    chair_weights = tsp.create_weighted_table(distance_weight, time_weight, distance_norm, time_norm)

    def tsp_server():

        start_time = datetime.now()
        listener = Listener(address)
        c = Committee(distance_table, time_table)

        # connects to all clients
        for i in range(0, num_clients):
            conn = listener.accept()
            name = conn.recv()
            c.add(conn, name)

        listener.close()

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
            best_solution, winner_name = c.get_best_solution(chair_weights)
            pipe.send((best_solution, "Solution Proposed By: {}".format(winner_name)))
            pipe.close()

        c.close_all()

    return Process(target=tsp_server)