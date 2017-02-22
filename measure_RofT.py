# measure_RofT.py
#
# A script for automating R(T) measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016

from anl_fridge_control.serial_connections import *
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
#parser_path = '/home/spt3g/pydfmux/firmware/mcgill/x86_64/parser'
#T_data_path = '/home/spt3g/ledgerman_output/20161005/down3.h5'
ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
R_data_path = '/home/spt3g/ledgerman_output/20161208/downm2m2.nc'
channel_of_interest = 'A'
PID_channel = 'A'

ChaseLS = LS.TempControl('/dev/ttyr18',  ['A', 'C1', 'D1', 'C2'])

ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)

#H4p = PS.PowerSupply(1,1)
#H4s = PS.PowerSupply(1,2)
H3ICp = PS.PowerSupply(2,1)
H3ICs = PS.PowerSupply(2,2)
H3UCp = PS.PowerSupply(3,1)
H3UCs = PS.PowerSupply(3,2)


# pydfmux stuff
hwm_file = '/home/spt3g/hardware_maps/hwm_anl_20161115_w109/hwm_anl_complete.yml'
y = pydfmux.load_session(open(hwm_file, 'r'))
rc=y['hardware_map'].query(pydfmux.ReadoutChannel)
bolos = y['hardware_map'].query(pydfmux.Bolometer)
ds = y['hardware_map'].query(pydfmux.Dfmux)

H3UCs.remote_set()
H3ICs.remote_set()

# unlatch the switches
print('Turning off switches...')
H3UCs.set_voltage(0.0)
H3ICs.set_voltage(0.0)
print('Heating up fridge...')
H3UCp.set_voltage(3.0)

ChaseLS.set_PID_temp(1, 0.500)
time.sleep(1)
ChaseLS.set_heater_range(2)

time.sleep(1)

while float(ChaseLS.get_temps()[channel_of_interest]) < 0.500:
	print ChaseLS.get_temps()[channel_of_interest]
	time.sleep(5)

H3UCp.set_voltage(0.00)
ChaseLS.set_PID_temp(1, wafer_high_temp)
time.sleep(5)

while float(ChaseLS.get_temps()[channel_of_interest]) < wafer_high_temp:
	print ChaseLS.get_temps()[channel_of_interest]
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
#H3UCs.set_voltage(4.0)
#H3ICs.set_voltage(4.0)
#time.sleep(5)
#print('Turning off switches...')
#H3UCs.set_voltage(0.0)
#H3ICs.set_voltage(0.0)
#time.sleep(60)


# do the ramp-down
#print('Starting ramp down...')
#current_temp = PID_high_temp
#ChaseLS.set_heater_range(2)
#time.sleep(1)
#ChaseLS.set_PID_temp(1,current_temp)
#time.sleep(2)
temps=[]

a=ChaseLS.get_temps()[channel_of_interest]
a
#while current_temp > PID_low_temp and float(a) > wafer_low_temp:
	#time.sleep(update_time)
	#current_temp = current_temp - (update_time * K_per_sec)
	#ChaseLS.set_PID_temp(1, current_temp)
	#print('Setting PID to %3.fmK'%(current_temp*1e3))
#	time.sleep(10)
#	a

try:
        while float(ChaseLS.get_temps()[channel_of_interest]) > wafer_low_temp:
		temps.append(ChaseLS.get_temps()[channel_of_interest])
                print ChaseLS.get_temps()[channel_of_interest]
                time.sleep(1)
except ValueError:
        print 'Give me a moment...'
        time.sleep(1)
        while float(ChaseLS.get_temps()[channel_of_interest]) > wafer_low_temp:
		temps.append(ChaseLS.get_temps()[channel_of_interest])
                print ChaseLS.get_temps()[channel_of_interest]
                time.sleep(1)
#time.sleep(300)

# do a ramp-up
#a
#time.sleep(1)
#print a
#time.sleep(1)
#print('Starting ramp up...')
#ChaseLS.set_PID_temp(1,PID_low_temp)
#time.sleep(1)
#ChaseLS.set_heater_range(2)
#time.sleep(1)
#current_temp=PID_low_temp
#time.sleep(1)
#while current_temp < PID_high_temp and float(a) < wafer_high_temp:
#	time.sleep(update_time)
#	current_temp = current_temp + (update_time * K_per_sec)
#	ChaseLS.set_PID_temp(1, current_temp)
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
