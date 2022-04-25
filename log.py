################################################################################
# TRAVELING SALESMAN PROBLEM - LOGGING FUNCTIONS
# Olga Koldachenko          okold525@mtroyal.ca
# COMP 5690                 Senior Computer Science Project
# Mount Royal University    Winter 2022
#
# This file holds several helper functions used in logging.
#
#       write(log_path, msg, timestamp = False, name = None)
# This writes a message to a text file. 
#
# PARAMETERS
# log_path:  - the path to the log file.
# msg:       - the message to write.
# timestamp: - if True, the message will be prefixed with the current time.
# name:      - if not None, the message will be prefixed with the name.
#
#
#       hr(log_path)
# This writes a horizontal rule to a text file.
#
# PARAMETERS
# log_path:  - the path to the log file.
#
#
#       write_csv(log_path, list)
# This writes a list of strings to a text file, separated by commas.
#
# PARAMETERS
# log_path:  - the path to the log file.
# list:      - the list of strings to write.
from datetime import datetime as dt

def write(log_path, msg, timestamp = False, name = None):
    try:
        with open(log_path, 'a') as f:
            s = ""
            if timestamp is not False:
                s = s + dt.now().strftime("%y-%m-%d %H:%M:%S") + " "
            if name is not None:
                s = s + name + " "
            s = s + msg + "\n"

            f.write(s)
            f.close()
    except:
        pass

def hr(log_path):
    write(log_path, "----------------------------------------")

def write_csv(log_path, list):
    write(log_path, ",".join(list))

class LogFile:
    def __init__(self, log_path):
        self.log_path = log_path
        try:
            f = open(self.log_path, 'w')
        except:
            print("Fail to create file:", self.log_path)
    
    def write(self, msg, timestamp = False, name = None):
        try:
            with open(self.log_path, 'a') as f:
                s = ""
                if timestamp is not False:
                    s = s + dt.now().strftime("%y-%m-%d %H:%M:%S") + " "
                if name is not None:
                    s = s + name + " "
                s = s + msg + "\n"

                f.write(s)
                f.close()
        except:
            pass

    def hr(self):
        self.write("----------------------------------------")

class CSVLogFile(LogFile):
    def write(self, list):
        LogFile.write(self, ",".join(list))