from datetime import datetime

import time
import tsp
from multiprocessing import Process
from multiprocessing.connection import Listener


def create_server(problem, sol_pipe, wait_time, num_clients, distance_weight=0.5, time_weight=0.5, num_rounds=3, address=("localhost", 6000)):

    start_time = datetime.now()

    # LOOKUP TABLE
    # creates lookup tables from the csv data
    distance_table, time_table, distance_norm, time_norm = tsp.create_lookup_tables(problem)
    chair_weights = tsp.create_weighted_table(distance_weight, time_weight, distance_norm, time_norm)
    #print(distance_norm)
    #print(time_norm)

    # STAKEHOLDER 
    stakeholder_list = []

    class Stakeholder():
        def __init__(self, conn, name):
            self.name = name
            self.conn = conn
            self.last_result = None

        def try_recv(self):
            if self.conn.poll():
                self.last_result = self.conn.recv()
                return True

            return False
        
        def print_solution(self, max_length):
            print(datetime.now(), "%-*s" % (max_length, self.name), self.last_result, tsp.fitness(chair_weights, self.last_result))

    # sends a message to all stakeholders in the stakeholder list
    def send_to_all(msg, log=None):
        if log != None:
            print(datetime.now(), log)

        for stakeholder in stakeholder_list:
            stakeholder.conn.send(msg)

    # requests data from all clients, then waits to receive it 
    def recv_from_all():
        send_to_all(("req_result"), 
            log="Requesting result from all clients.")

        waiting_list = []
        for stakeholder in stakeholder_list:
            waiting_list.append(stakeholder)

        while waiting_list != []:
            for stakeholder in waiting_list:
                if stakeholder.try_recv():  # if you successfully get data
                    waiting_list.remove(stakeholder)

    def get_best_solution():
        result_list = list(map(lambda x: x.last_result, stakeholder_list))
        return tsp.best_solution(chair_weights, result_list)


    # SERVER FUNCTION
    def tsp_server():

        listener = Listener(address)

        # connects to all clients
        for i in range(0, num_clients):
            conn = listener.accept()
            name = conn.recv()
            stakeholder_list.append(Stakeholder(conn, name))

        # gets the max name length for printing        
        max_length = 0
        for stakeholder in stakeholder_list:
            max_length = max(max_length, len(stakeholder.name))

        # rounds
        best_solution = None
        for i in range(0, num_rounds):
            print(datetime.now(), "Beginning round", i)
            if i == 0:
                send_to_all(("init", distance_norm, time_norm), 
                    log="Server sent problem to clients")
            else:
                send_to_all(("continue", best_solution), 
                    log="Sending best solution to all clients.")

            time.sleep(wait_time)

            recv_from_all()
            for stakeholder in stakeholder_list:
                stakeholder.print_solution(max_length)

            best_solution = get_best_solution()
            print()
            print(  "BEST SOLUTION FROM ROUND", i)
            print(  best_solution)
            print(  "Distance:", tsp.total(distance_table,best_solution))
            print(  "Time", tsp.total(time_table,best_solution))
            print()

            if wait_time > 0:
                time.sleep(2) #short pause between rounds, but only if waiting
        
        send_to_all(("stop"))
        print(datetime.now(), "Sent stop!")
        total_time = (datetime.now() - start_time).total_seconds()
        print("Total time:", total_time)


        sol_pipe.send(best_solution)

    return Process(target=tsp_server)