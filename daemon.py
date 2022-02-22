#!/bin/python

# ALLOWED IMPORTS
import signal
import os
import sys
import datetime

# GLOBAL VARIABLES
daemon_quit = False  # Use this variable for your loop
PIPE_FILE = "/tmp/cald_pipe"
ERROR_LOG = "/tmp/cald_err.log"
DATA_LINK = "/tmp/calendar_link"

database = os.path.abspath("./cald_db.csv")
snapshot = []

class Event:
    def __init__(self, date, name, description=""):
        self.date = date
        self.name = name
        self.description = description

    def __str__(self):
        if len(self.description) == 0:
            return "{},{}\n".format(self.date, self.name)
        return "{},{},{}\n".format(self.date, self.name, self.description)

    def __repr__(self):
        if len(self.description) == 0:
            return "{},{}\n".format(self.date, self.name)
        return "{},{},{}\n".format(self.date, self.name, self.description)

    # this function constructs an event from a line from the csv file
    def parse_str_from_csv(line: str):
        tokens = line.split(",")
        if len(tokens) < 3:
            return None
        # check if date is valid
        if check_date(tokens[0]):
            date = tokens[0]
        else:
            return None
        if len(tokens) == 2:
            name = tokens[1].strip()
            return Event(date, name, "")
        # event description given
        else:
            name = tokens[1]
            description = tokens[2].strip()
            return Event(date, name, description)

    # this function constructs an event from a line from the csv file
    def parse_str_pipe(line: str):
        tokens = line.split(" ")
        if len(tokens) < 3:
            print("Missing event name", file=ERROR_LOG)
            return None
        # check if date is valid
        if check_date(tokens[1]):
            date = tokens[1]
        else:
            print("Unable to parse date", file=ERROR_LOG)
            return None
        name = tokens[2]
        if len(tokens) == 3:
            return Event(date, name, "")
        # event description given
        else:
            description = tokens[3].strip()
            return Event(date, name, description)

# HELPER FUNCTIONS
def quit_gracefully(signum, frame):  # Do not modify or remove this handler
    global daemon_quit
    daemon_quit = True

def read_csv_database():
    global database
    ls = []
    f = open(database, "r")
    lines = f.readlines()
    for l in lines:
        event = Event.parse_str_from_csv(l)
        if event is None:
            continue
        ls.append(event)
    f.close()
    return ls

def save_link():
    f = open(DATA_LINK, "w")
    global database
    if len(sys.argv) > 1:  # database path given as first arg of daemon
        database = os.path.abspath(sys.argv[1])
    f.write(database)
    f.close()
    try:
        # file already exists, load
        loaded_snapshot = read_csv_database()
    except FileNotFoundError:
        # file doesn't exist, create an empty one
        loaded_snapshot = []
        with open(database, "w") as f:
            f.close()
    global snapshot
    snapshot = loaded_snapshot


# date should be in DD-MM-YYYY
def check_date(d: str):
    if len(d) == 10:
        day, month, year = d.split("-")
        try:
            datetime.date(int(year), int(month), int(day))
            return True
        except ValueError:
            print("Unable to parse date", file=ERROR_LOG)
            return False
    else:
        return False

def update_database():
    f = open(database, "w")
    f.writelines([str(event) for event in snapshot])
    f.close()

def get_key(name: str, date: str):
    return name + "|" + date

def look_up_event(key: str):
    for e in snapshot:
        if get_key(e.name, e.date) == key:
            return True, e
    return False, None

# FUNCTIONS FOR EACH COMMAND 
def add_event(line: str):
    event = Event.parse_str_pipe(line)
    if event is None:
        print("Missing event name", file=ERROR_LOG)
        return
    k = get_key(event.name, event.date)
    found, existing_event = look_up_event(k)
    if found:
        print("Unable to add, event already exists", file=ERROR_LOG)
        return
    snapshot.append(event)
    update_database()

def delete_event(line: str):
    # split string into tokens
    tokens = line.split(" ")
    if len(tokens) < 3:
        print("Missing event name", file=ERROR_LOG)
        return

    # check if date is valid
    if check_date(tokens[1]):
        date = tokens[1]
    else:
        return

    name = tokens[2]

    k = get_key(name, date)
    found, existing_event = look_up_event(k)
    if not found:
        return

    snapshot.remove(existing_event)
    update_database()

def update_event(line: str):
    # split string into tokens
    tokens = line.split(" ")
    if len(tokens) < 4:
        print("Not enough arguments given", file=ERROR_LOG)
        return

    # check if date is valid
    if check_date(tokens[1]):
        date = tokens[1]
    else:
        return
    old_name = tokens[2]
    new_name = tokens[3]

    k = get_key(old_name, date)

    found, old_event = look_up_event(k)
    if not found:
        print("Unable to update, event does not exist", file=ERROR_LOG)
        return

    description = ""
    if len(tokens) > 4:
        description = tokens[4]

    old_event.name = new_name
    old_event.description = description.strip()

    update_database()

# DRIVER CODE
def run():
    # Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)

    # Creating a named pipe
    if not os.path.exists(PIPE_FILE):
        os.mkfifo(PIPE_FILE)

    save_link()

    # Main loop
    while not daemon_quit:
        # Open named pipe and csv
        pipe = open(PIPE_FILE, "r")

        # Read from named pipe - [0] = operation code, [1:] event
        recv_cmd_line = pipe.readline()
        main_cmd = recv_cmd_line.split()[0]

        # Depending on what received_command stores, call the appropriate function
        if main_cmd == "ADD":
            add_event(recv_cmd_line)
        elif main_cmd == "DEL":
            delete_event(recv_cmd_line)
        elif main_cmd == "UPD":
            update_event(recv_cmd_line)

    # Close the named pipe
    pipe.close()

if __name__ == '__main__':
    run()