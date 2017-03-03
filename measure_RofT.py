# measure_RofT.py
#
# A script for automating R(T) measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016

import anl_fridge_control.serial_connections as sc
import he10_fridge_control.control.gettemp as gt
import pydfmux
import time
import os
import datetime
import numpy as npged
import cPickle as pickle
import subprocess

# user params
PID_high_temp = 0.650
PID_low_temp = 0.400
wafer_high_temp = 0.650
wafer_low_temp = 0.400
K_per_sec = 1e-4
update_time = 10
overbias_amplitude = 0.0002

logfile =
#parser_path = '/home/spt3g/pydfmux/firmware/mcgill/x86_64/parser'
#T_data_path = '/home/spt3g/ledgerman_output/20161005/down3.h5'
ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
R_data_path = '/home/spt3g/ledgerman_output/20161208/downm2m2.nc'

# pydfmux stuff
hwm_file = '/home/spt3g/hardware_maps/hwm_anl_20161115_w109/hwm_anl_complete.yml'
y = pydfmux.load_session(open(hwm_file, 'r'))
rc=y['hardware_map'].query(pydfmux.ReadoutChannel)
bolos = y['hardware_map'].query(pydfmux.Bolometer)
ds = y['hardware_map'].query(pydfmux.Dfmux)

sc.He3UCs.remote_set()
sc.He3ICs.remote_set()

# unlatch the switches
print('Turning off switches...')
sc.He3UCs.set_voltage(0.0)
sc.He3ICs.set_voltage(0.0)

while float(gt.gettemp(logfile, 'He3 UC Switch'))>2.00:
	time.sleep(10)
while float(gt.gettemp(logfile, 'He3 IC Switch'))>2.00:
	time.sleep(10)

print('Heating up fridge...')
sc.He3UCp.set_voltage(3.0)

sc.ChaseLS.set_PID_temp(1, 0.500)
time.sleep(1)
sc.ChaseLS.set_heater_range(2)

time.sleep(1)

while float(gt.gettemp(logfile, 'UC Head')) < 0.500:
	print gt.gettemp(logfile, 'UC Head')
	time.sleep(5)

sc.He3UCp.set_voltage(0.00)
sc.ChaseLS.set_PID_temp(1, wafer_high_temp)
time.sleep(5)

while float(gt.gettemp(logfile, 'UC Head')) < wafer_high_temp:
	print gt.gettemp(logfile, 'UC Head')
	time.sleep(5)

time.sleep(600)

# overbias bolometers
ds.clear_all()
ds.clear_dan()
overbias_results = bolos.overbias_and_null(cold_overbias=False,serialize=True,carrier_amplitude = overbias_amplitude)


# start ledgerman
#proc_parser = subprocess.Popen([parser_path, '-d', T_data_path])
proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_file, R_data_path])
#print datetime.datetime.now()



# latch the switches to help with cooldown
#print('Turning on switches...')
#sc.He3UCs.set_voltage(4.0)
#sc.He3ICs.set_voltage(4.0)
#time.sleep(5)
#print('Turning off switches...')
#sc.He3UCs.set_voltage(0.0)
#sc.He3ICs.set_voltage(0.0)
#time.sleep(60)


# do the ramp-down
#print('Starting ramp down...')
#current_temp = PID_high_temp
#sc.ChaseLS.set_heater_range(2)
#time.sleep(1)
#sc.ChaseLS.set_PID_temp(1,current_temp)
#time.sleep(2)
temps=[]

a=gt.gettemp(logfile, 'UC Head')
a
#while current_temp > PID_low_temp and float(a) > wafer_low_temp:
	#time.sleep(update_time)
	#current_temp = current_temp - (update_time * K_per_sec)
	#sc.ChaseLS.set_PID_temp(1, current_temp)
	#print('Setting PID to %3.fmK'%(current_temp*1e3))
#	time.sleep(10)
#	a

try:
        while float(gt.gettemp(logfile, 'UC Head')) > wafer_low_temp:
		temps.append(gt.gettemp(logfile, 'UC Head'))
                print gt.gettemp(logfile, 'UC Head')
                time.sleep(1)
except ValueError:
        print 'Give me a moment...'
        time.sleep(1)
        while float(gt.gettemp(logfile, 'UC Head')) > wafer_low_temp:
		temps.append(gt.gettemp(logfile, 'UC Head'))
                print gt.gettemp(logfile, 'UC Head')
                time.sleep(1)
#time.sleep(300)

# do a ramp-up
#a
#time.sleep(1)
#print a
#time.sleep(1)
#print('Starting ramp up...')
#sc.ChaseLS.set_PID_temp(1,PID_low_temp)
#time.sleep(1)
#sc.ChaseLS.set_heater_range(2)
#time.sleep(1)
#current_temp=PID_low_temp
#time.sleep(1)
#while current_temp < PID_high_temp and float(a) < wafer_high_temp:
#	time.sleep(update_time)
#	current_temp = current_temp + (update_time * K_per_sec)
#	sc.ChaseLS.set_PID_temp(1, current_temp)
#	print('Setting PID to %3.fmK'%(current_temp*1e3))


#while float(a) < wafer_high_temp:
#	print a
#	time.sleep(30)

proc_ledgerman.terminate()
#proc_parser.terminate()
#print datetime.datetime.now()

f=open('/home/spt3g/ledgerman_output/20161206/down_temps.pkl','w')
pickle.dump(temps,f)
f.close()
