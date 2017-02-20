README
===============
Lauren Saunders
February 20, 2017

This repository contains various Python scripts and tools for running the He10 cryostat at Argonne National Laboratory.

Connection setup
----------------
Relevant Files:

- Driver files (xxxx.txt)

- lakeshore.py

- powersupply.py

At present, the connections to the power supplies and PID heater are controlled through two python modules, powersupply.py and lakeshore.py.  Each of these creates a class (PowerSupply or TempControl), which opens a serial connection to the remote electronics.  powersupply.py must also be supplied driver files (.txt) which specify the type of connection and the remote interface commands.  Here, those driver files are stored as He4p.txt, He4s.txt, He3ICp.txt, He3ICs.txt, He3UCp.txt, and He3UCs.txt.

At present, the powersupply class is set up to retrieve text files in tuplet (box number, output number).  The He4 power supply is box number 1, He3IC power supply is box number 2, and He3UC power supply is box number 3; the pump is always output 1, and the switch is always output 2.  This can be changed at the end of the powersupply.py file.

To create each of these connections with the current ANL setup from an ipython session, you can use:
::
  import powersupply as PS
  import lakeshore as LS
  
  He4p=PS.PowerSupply(1,1)
  He4s=PS.PowerSupply(1,2)
  He3ICp=PS.PowerSupply(2,1)
  He3ICs=PS.PowerSupply(2,2)
  He3UCp=PS.PowerSupply(3,1)
  He3UCs=PS.PowerSupply(3,2)
  
  ChaseLS=LS.TempControl('/dev/ttyr18',['A','B','C1','C2'])
  
Other modules create these connections for you, so you will generally not need to write this out.  However, if you wish to change the setup, you will need to make sure that all other files that control temperature are written correctly for your current setup.

Basic fridge control functions
------------------------------
basic_functions.py contains various functions for day-to-day fridge functions.

- basic_functions.zero_everything(): Turns all voltages to 0.00, and turns off the PID heater.

  - Parameters: None
  - Returns: None

- basic_functions.autocycle(): Runs an automated cycle (takes about 9 hours)

  - Parameters: current temperature logfile, start (default=False)
    - The current logfile is whatever is created by the logger.  You should be using the file called he10_logs/xxxx_read.h5
    - start=True tells the computer to run the start_of_day function after completing the cycle.
  - Returns: None

- basic_functions.start_of_day(): Warms the UC Head to 650mK, then heats and tunes SQUIDs and takes a rawdump.

  - Parameters: current temperature logfile, set_squid_feedback (default=False), set_gain (default=False)
    - The current logfile is whatever is created by the logger.  You should be using the file called he10_logs/xxxx_read.h5
    - set_squid_feedback is a pydfmux call, which sets SQUID feedback if True
    - set_gain is a pydfmux call, which sets gain
  - Returns: some output directories for heating and tuning

- basic_functions.finish_cycle(): Runs the part of a cycle that waits for the heat exchanger temperature to rise and then cools the fridge to base.

  - Called by other functions; can be called if you are manually calling part of the cycle (i.e. if something goes wrong midway through)
  - Parameters: current temperature logfile
    - The current logfile is whatever is created by the logger.  You should be using the file called he10_logs/xxxx_read.h5
  - Returns: None
    
Pending update: autocycle will become an independent python script

Wafer testing
-------------
Some functions for measuring and analyzing R(T) and G(T) are included.

Miscellaneous
-------------
There are also some miscellaneous helper scripts for specific extra testing.

  sinusoidal.py: generates sinusoidal voltages through function sinuvolt()
    Parameters: name=PS name, A=amplitude, freq=frequency, y=offset from 0, tint=time interval, R=resistance, t0=initial time (default=0) 
