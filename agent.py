################################################################################
# AGENT
# Olga Koldachenko
#
# A framework for an agent, running a work function in one thread and a
# communication function in another.
#
#       PARAMETERS
# address: the address for external communcation, defaults ('localhost', 6000)
# server: a boolean on whether or not the agent is a server, defaults to False.
#         a server will listen for connections with the Listener class, while
#         a client will connect to a single server
# work_function: the function to run in the work thread
# comm_function: the function to run in the communication thread
# work_kwargs: a dictionary of keyword arguments passed to the worker
# comm_kwargs: a dictionary of keyword arguments passed to the communicator
#
# When creating functions for the Agent class, they must take a single parameter
# self, referencing either the Worker or Communicator object they're attributed.
#
# This gives the function access to certain objects:
#
#       WORKER
# comm: a Connection object to the Agent's Communicator
# kwargs: a dictionary with these pre-defined objects
#   - close_comms: an Event object notifying closed external communications
#
#       COMMUNICATOR
# communicator: an object to handle external communications
#   - this is a Listener if server=True when initializing the Agent
#   - this is a Client if server=False when initializing the Agent
# worker: a Connection object to the Agent's Worker
# kwargs: a dictionary with these pre-defined objects
#   - close_comms: an Event object notifying closed external communications

from multiprocessing import Process
from threading import Thread, Event
from multiprocessing.connection import Listener, Client, Pipe
import time

class Agent(Process):
    def __init__(self, address = ('localhost', 6000), server = False,
        work_function = None, comm_function = None):
        Process.__init__(self)
        
        self.worker = None
        self.comm = None

        close_comms = Event()
        self.work_kwargs = {}
        self.comm_kwargs = {}
        self.work_kwargs["close_comms"] = close_comms
        self.comm_kwargs["close_comms"] = close_comms
        
        work_conn, comm_conn = Pipe()

        if work_function != None:
            self.worker = self.Worker(work_conn, work_function, self.work_kwargs)

        if comm_function != None:
            self.comm = self.Communicator(address, server, comm_conn, comm_function, self.comm_kwargs)

        
    
    def run(self):
        if self.comm != None:
            self.comm.start()
        
        if self.worker != None:
            self.worker.start()

        if self.comm != None:
            self.comm.join()

        if self.worker != None:
            self.worker.join()

    class Worker(Thread):
        def __init__(self, comm, function, kwargs):
            Thread.__init__(self, daemon = True)

            self.comm = comm
            self.function = function
            self.kwargs = kwargs

        def run(self):
            self.function(self)
            self.comm.close()

    class Communicator(Thread):
        def __init__(self, address, server, worker, function, kwargs):
            Thread.__init__(self, daemon = True)

            self.worker = worker
            self.kwargs = kwargs

            self.communicator = None
            if server:
                self.communicator = Listener(address)
            else:
                while self.communicator == None:
                    try:
                        self.communicator = Client(address)
                    except:
                        time.sleep(2)

            self.function = function

        def run(self):
            self.function(self)
            self.communicator.close()
            self.worker.close()