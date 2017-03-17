# measure_GofT.py
#
# Script for using PID control feature of Lakeshore 350 in order to automatically take G(T)
# measurements (Psat as a function of T). This script isn't totally cryostat-independent,
# but it should be nearly so if you are using a heater close to your UC head to PID control
# the stage temperature, wait for a separate thermometry near the wafer to stabilize between
# measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016

import pydfmux
from anl_fridge_control.serial_connections import *
import os,time
import datetime
import numpy as np
from matplotlib.pylab import switch_backend
import cPickle as pickle
from pydfmux.core.utils.conv_functs import build_hwm_query
import anl_fridge_control.serial_connections as sc

import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt

logfile = '/home/spt3g/he10_logs/20170302_again_read.h5'
hwm_dir='/home/spt3g/hardware_maps/hwm_anl_20170306_W169_and_Rboards/hwm_anl_proto.yml'

hwm=pydfmux.load_session(open(hwm_dir))['hardware_map']
ds=hwm.query(pydfmux.Dfmux)
sqcbs=hwm.query(pydfmux.SQUIDController)
squids=hwm.query(pydfmux.SQUID)
bolos = hwm.query(pydfmux.Bolometer)
rm=hwm.query(pydfmux.ReadoutModule)
d=ds[0]


# cryostat-specific settings
setpoints = np.linspace(0.300, 0.600, 7)

print 'Starting G(T)'

#sc.He3ICp.set_voltage(0)
#sc.He3UCp.set_voltage(0)
#sc.He3ICs.set_voltage(0)
#sc.He3UCs.set_voltage(0)
#sc.ChaseLS.set_PID_temp(1, 0.500)
#time.sleep(1)
#sc.ChaseLS.set_heater_range(2)
#while float(gt.gettemp(logfile, 'UC Head'))<0.500:
#    time.sleep(10)
#sc.ChaseLS.set_PID_temp(1,0.650)
#time.sleep(1)
#sc.ChaseLS.set_heater_range(3)
#time.sleep(1)
#while float(gt.gettemp(logfile, 'UC Head'))<0.650:
#    time.sleep(20)
#time.sleep(300)

#if 'good_bolos' in locals():
#	overbias_results = good_bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)
#else:
#	overbias_results = bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)

#print 'Overbiasing'
#ds.clear_all()
#ds.clear_dan()
#bolos.overbias_and_null(cold_overbias=False, serialize=True, carrier_amplitude=0.015, scale_by_frequency=True)

waferstarttemps = np.zeros(len(setpoints))
measurestarttimes = np.zeros(len(setpoints))
waferstoptemps = np.zeros(len(setpoints))
measurestoptimes = np.zeros(len(setpoints))

sc.He3ICp.set_voltage(0)
sc.He3ICs.set_voltage(0)
sc.He3UCp.set_voltage(0)
sc.He3UCs.set_voltage(0)

for jtemp in range(len(setpoints)):
    print setpoints[jtemp]
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))

    sc.ChaseLS.set_PID_temp(1, setpoints[jtemp])
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    time.sleep(1)
    sc.He3UCs.set_voltage(3.00)
    sc.He3ICs.set_voltage(4.00)
    while float(gt.gettemp(logfile, 'UC Head'))>(setpoints[jtemp]+0.05):
	time.sleep(60)
    sc.He3UCs.set_voltage(0.00)
    sc.He3ICs.set_voltage(0.00)
    time.sleep(5*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and nAttempts < 45:
        time.sleep(20)
        recenttemps.append(int(float(gt.gettemp(logfile, 'UC Head')*1e3)))
        nAttempts += 1
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] - recenttemps[-4]))
    if nAttempts == 45:
        sc.ChaseLS.set_heater_range(0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    waferstarttemps[jtemp] = gt.gettemp(logfile, 'UC Head')
    measurestarttimes[jtemp] = time.time()
    print waferstarttemps

    time.sleep(300)

    alive = bolos.find_alive_bolos()
    noise_results_before = alive.dump_info()

    drop_bolos_results =  bolos.drop_bolos(monotonic=True,A_STEP_SIZE=0.000015,TOLERANCE=0.05)
    waferstoptemps[jtemp] = gt.gettemp(logfile, 'UC Head')
    measurestoptimes[jtemp] = time.time()
    print waferstoptemps

    # save the data to a pickle file, rewriting after each acquisition
    f = file('/home/spt3g/output/20170317/G_temp_data_20170317.pkl', 'w')
    pickle.dump([waferstarttemps, measurestarttimes, waferstoptemps, measurestoptimes], f)
    f.close()

    alive = bolos.find_alive_bolos()
    noise_results_after = alive.dump_info()

    print 'Raising temperature for overbias.'
    sc.ChaseLS.set_PID_temp(1, 0.500)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    while float(gt.gettemp(logfile, 'UC Head'))<0.500:
        time.sleep(20)

    sc.ChaseLS.set_PID_temp(1,0.650)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(3)
    time.sleep(1)
    while float(gt.gettemp(logfile, 'UC Head'))<0.650:
	time.sleep(10)
    time.sleep(600)

    ds.clear_all()
    ds.clear_dan()
    bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.015, scale_by_frequency=True)

#    if 'good_bolos' in locals():
#    	overbias_results = good_bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)
#    else:
#    	overbias_results = bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)


sc.ChaseLS.set_heater_range(0)
time.sleep(1)
sc.ChaseLS.set_PID_temp(1, 0.000)
print waferstarttemps
print measurestarttimes
print waferstoptemps
print measurestoptimes

#zero_everything()
