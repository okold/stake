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