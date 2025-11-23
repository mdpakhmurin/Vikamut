from datetime import datetime


def is_delete(msg):
    msg_raw = str(msg)

    if ("пупупу" in msg_raw):
        print(datetime.now(), "\t", "F: пупупу")
        return True
    
    return False