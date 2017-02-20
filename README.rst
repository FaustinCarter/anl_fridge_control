README
===============
Lauren Saunders
February 20, 2017

This repository contains various Python scripts and tools for running the He10 cryostat at Argonne National Laboratory.

Basic fridge control functions
------------------------------
basic_functions.py contains various functions for day to day fridge functions.

  zero_everything(): A function that turns all voltages to 0.00, and turns off the PID heater.
    Parameters: None
    Returns: None

  autocycle(): Runs an automated cycle (takes about 9 hours)
    Parameters: current temperature logfile
    Returns: None

  finish_cycle(): Runs the part of a cycle that waits for the heat exchanger temperature to rise and then cools the fridge to base.  Called by other functions.

  start_of_day(): Warms the UC Head to 650mK, then heats and tunes SQUIDs and takes a rawdump.
    Parameters: current temperature logfile
    Returns: some output directories for heating and tuning
