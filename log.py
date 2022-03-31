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