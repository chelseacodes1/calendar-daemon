import os
import sys
import datetime 

# GLOBAL VARIABLES
PIPE_FILE = "/tmp/cald_pipe"
DATA_LINK = "/tmp/calendar_link"

class Event:
    def __init__(self, date, name, description=""):
        self.date = date
        self.name = name
        self.description = description

    def __str__(self):
        if len(self.description) == 0:
            return "{},{}".format(self.date, self.name)
        return "{},{},{}".format(self.date, self.name, self.description)

    def __repr__(self):
        if len(self.description) == 0:
            return "{},{}".format(self.date, self.name)
        return "{},{},{}".format(self.date, self.name, self.description)

    # this function constructs an event from a line from the csv file
    def parse_str_from_csv(line: str):
        tokens = line.split(",")
        if len(tokens) < 2:
            return None
        # check if date is valid
        if check_date(tokens[0]):
            date = tokens[0]
        else:
            return None
        name = tokens[1]
        if len(tokens) == 2:
            return Event(date, name, "")
        # event description given
        elif len(tokens) == 3:
            description = tokens[2]
            return Event(date, name, description)

# HELPER FUNCTIONS
# date should be in DD-MM-YYYY
def check_date(d: str):
    if len(d) == 10:
        day, month, year = d.split("-")
        try:
            datetime.date(int(year), int(month), int(day))
            return True
        except ValueError:
            sys.stderr.write("Unable to parse date\n")
            return False
    else:
        sys.stderr.write("Unable to parse date\n")
        return False
    
def parse_date(date: str):
    if len(date) == 10:
        day, month, year = date.split("-")
        try:
            return datetime.date(int(year), int(month), int(day))
        except ValueError:
            sys.stderr.write("Unable to parse date\n")
    else:
        sys.stderr.write("Unable to parse date\n")
    
def check_valid_interval(start: datetime, end: datetime):
    if start <= end:
        return True
    else:
        return False


def read_csv_database():
    try:
        f = open(DATA_LINK, "r")
        csv_path = f.readline()

    except FileNotFoundError:
        sys.stderr.write("Unable to process calendar database\n")
        return

    ls = []
    f1 = open(csv_path, "r")
    lines = f1.readlines()
    for l in lines:
        event = Event.parse_str_from_csv(l)
        if event is None:
            continue
        ls.append(event)
    f.close()
    f1.close()
    return ls

# GET COMMAND FUNCTIONS  
# DATE - search database for all events on a specific date 
def get_event_by_date(target_dates):
    # check if dates are valid
    valid_dates = []
    for t in target_dates:
        if check_date(t):
            valid_dates.append(t)

    events = []
    ls = read_csv_database()
    for e in ls:
        for d in valid_dates:
            if d == e.date:
                events.append("{} : {} : {}".format(d, e.name, e.description))

    for e in events:
        print(e.strip())
                
# INTERVAL - given 2 dates, output all events between these dates
def get_event_by_interval(start: str, end: str):
    events = []
    ls = read_csv_database()

    # check if dates are valid
    if (check_date(start) and check_date(end)):

        # check if date interval is correct
        if check_valid_interval:
            start_date = parse_date(start)
            end_date = parse_date(end)

            # iterate through csv
            for e in ls:
                if start_date <= parse_date(e.date) <= end_date:
                    events.append("{} : {} : {}".format(e.date, e.name, e.description))

            for e in events:
                print(e.strip())

        else:
            sys.stderr.write("Unable to Process, Start date is after End date\n")
    else:
        sys.stderr.write("Unable to parse date\n")

# NAME - search database for events with partial match of name 
def get_event_by_name(target_names): 
    events = []

    ls = read_csv_database()
    for e in ls:
        for n in target_names:
            if e.name.startswith(n):
                events.append("{} : {} : {}".format(e.date, e.name, e.description))

    for e in events:
        print(e.strip())

# ERROR HANDLING FOR ADD, DEL, UPD
def check_valid_cmd_line_args(args):
    date_correct = True
    event_name_exist = True
    if len(args) < 3:
        if len(args) < 2:
            date_correct = False
        else:
            if not check_date(args[1]):
                date_correct = False
            event_name_exist = False
    if not date_correct and not event_name_exist:
        sys.stderr.write("Missing event name\n")
        return False
    elif date_correct and not event_name_exist:
        sys.stderr.write("Multiple errors occur\n")
        return False
    elif not date_correct and event_name_exist:
        sys.stderr.write("Unable to parse date\n")
        return False
    return True

# DRIVER CODE 
def run():
    if len(sys.argv) > 1: 
        main_cmd = sys.argv[1]
        if main_cmd == "GET":
            get_cmd = sys.argv[2]
            if get_cmd == "DATE":
                get_event_by_date(sys.argv[3:])
            elif get_cmd == "INTERVAL":
                if len(sys.argv) == 5:
                    get_event_by_interval(sys.argv[3], sys.argv[4])
            elif get_cmd == "NAME":
                if len(sys.argv) < 4:
                    sys.stderr.write("Please specify an argument\n")
                get_event_by_name(sys.argv[3:]) 
        
        elif main_cmd == "ADD" or main_cmd == "DEL" or main_cmd == "UPD":
            pass
            # Check if command line args are valid before writing to the pipe 
            if (check_valid_cmd_line_args(sys.argv[1:])):
                if os.path.exists(PIPE_FILE):
                    pipe = open(PIPE_FILE, "w")
                    
                    # Join command line arguments and write to the pipe
                    cmd_line = " ".join(sys.argv[1:])
                    pipe.write(cmd_line)
                    pipe.close()

if __name__ == '__main__':
    run()