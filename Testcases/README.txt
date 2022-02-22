The directory 'Testcases' contains the testcases for Tasks 1 and 2.
Within the 'Testcases' directory there are 4 subdirectories; one for each command (add, delete, get and update) which contain .in and .out files testing all execution paths in the calendar and daemon programs.
For the purposes of testing, each subdirectory contains a cald_db.csv file.
The .in files represent inputs into the 'calendar.py' program and the .out files represent outputs depending on the action argument provided.
For the GET command, the 'calendar.py' program passes in input represented by the .in files, handles the calls in the program itself and produces standard output represented in the .out files. 
For ADD, UPD and DEL commands, the 'calendar.py' program writes data from .in files to the named pipe and handles these calls in the 'daemon.py' program. The output of these commands are entries in the csv database which are represented in the .out files. 
Additionally, the error messages for the testcases are stores in 'stderr.txt' file within each subdirectory. 