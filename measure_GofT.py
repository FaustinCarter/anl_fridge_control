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
import he10_fridge_control.Lauren.lakeshore as LS
import he10_fridge_control.Lauren.powersupply as PS
import os,time
import datetime
import numpy as np
from matplotlib.pylab import switch_backend
import cPickle as pickle
from pydfmux.core.utils.conv_functs import build_hwm_query
from he10_fridge_control.Lauren.basic_functions import start_of_day
from he10_fridge_control.Lauren.basic_functions import zero_everything

hwm_dir='/home/spt3g/hardware_maps/hwm_anl_20161207_w132/hwm_anl_complete.yml'
board='0135'

hwm=pydfmux.load_session(open(hwm_dir))['hardware_map']
ds=hwm.query(pydfmux.Dfmux)
sqcbs=hwm.query(pydfmux.SQUIDController)
squids=hwm.query(pydfmux.SQUID)
bolos = hwm.query(pydfmux.Bolometer)
rm=hwm.query(pydfmux.ReadoutModule)
d=ds[0]

He4p = PS.PowerSupply(1,1)
He4s = PS.PowerSupply(1,2)
He3ICp = PS.PowerSupply(2,1)
He3ICs = PS.PowerSupply(2,2)
He3UCp = PS.PowerSupply(3,1)
He3UCs = PS.PowerSupply(3,2)

gbolos=[]
for bb in bolos.all():
    if (bb.iceboard != None) and (bb.iceboard.serial !=None):
#        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==2):
#            gbolos.append(bb)
#        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==3):
#            gbolos.append(bb)
#        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==4):
#            gbolos.append(bb)
        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==1):
            gbolos.append(bb)
        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==2):
            gbolos.append(bb)
        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==3):
            gbolos.append(bb)
#        if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==4):
#            gbolos.append(bb)

#gbolos.remove(bolos.all()[174])
#gbolos.remove(bolos.all()[215])


good_bolos=build_hwm_query(gbolos)
good_bolos=good_bolos.filter(pydfmux.Bolometer.overbias==True)
# cryostat-specific settings
setpoints = np.linspace(0.280, 0.600, 9)
PID_channel = 'A'
channel_of_interest = 'A'

ChaseLS = LS.TempControl('/dev/ttyr18',  ['A', 'C1', 'D1', 'C2'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)

print 'Starting G(T)'

He3ICp.set_voltage(0)
He3UCp.set_voltage(0)
He3ICs.set_voltage(0)
He3UCs.set_voltage(0)
ChaseLS.set_PID_temp(1,0.500)
time.sleep(1)
ChaseLS.set_heater_range(2)
time.sleep(300)
ChaseLS.set_PID_temp(1,0.650)
time.sleep(1)
ChaseLS.set_heater_range(3)
time.sleep(1)
while float(ChaseLS.get_temps()[channel_of_interest])<0.650:
	time.sleep(20)
time.sleep(300)

#if 'good_bolos' in locals():
#	overbias_results = good_bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)
#else:
#	overbias_results = bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)

print 'Overbiasing'
execfile('/home/spt3g/pydfmux/users/anluser/anl_master_script.py')

waferstarttemps = np.zeros(len(setpoints))
measurestarttimes = np.zeros(len(setpoints))
waferstoptemps = np.zeros(len(setpoints))
measurestoptimes = np.zeros(len(setpoints))

He3ICp.set_voltage(0)
He3ICs.set_voltage(0)
He3UCp.set_voltage(0)
He3UCs.set_voltage(0)

for jtemp in range(len(setpoints)):
    print setpoints[jtemp]
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))

    ChaseLS.set_PID_temp(1, setpoints[jtemp])
    time.sleep(1)
    ChaseLS.set_heater_range(2)
    time.sleep(1)
    He3UCs.set_voltage(3.00)
#    He3ICs.set_voltage(4.00)
    while float(ChaseLS.get_temps()[channel_of_interest])>(setpoints[jtemp]+0.05):
	time.sleep(60)
    He3UCs.set_voltage(0.00)
#    He3ICs.set_voltage(0.00)
    time.sleep(5*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and \
          nAttempts < 45:
        time.sleep(20)
        recenttemps.append(float(ChaseLS.get_temps()[channel_of_interest]))
        nAttempts = nAttempts + 1
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] - recenttemps[-4]))
    if nAttempts == 45:
        ChaseLS.set_heater_range(0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    waferstarttemps[jtemp] = ChaseLS.get_temps()[channel_of_interest]
    measurestarttimes[jtemp] = time.time()
    print waferstarttemps

    time.sleep(300)

    drop_bolos_results =  good_bolos.drop_bolos(monotonic=True,A_STEP_SIZE=0.000015,TOLERANCE=0.05)
    waferstoptemps[jtemp] = ChaseLS.get_temps()[channel_of_interest]
    measurestoptimes[jtemp] = time.time()
    print waferstoptemps

    # save the data to a pickle file, rewriting after each acquisition
    f = file('/home/spt3g/output/20161213/G_temp_data_20161213.pkl', 'w')
    pickle.dump([waferstarttemps, measurestarttimes, waferstoptemps, measurestoptimes], f)
    f.close()

    print 'Raising temperature for overbias.'
    ChaseLS.set_PID_temp(1, 0.500)
    time.sleep(1)
    ChaseLS.set_heater_range(2)
    time.sleep(300)

    ChaseLS.set_PID_temp(1,0.650)
    time.sleep(1)
    ChaseLS.set_heater_range(3)
    time.sleep(1)
    while float(ChaseLS.get_temps()[channel_of_interest])<0.650:
	time.sleep(10)
    time.sleep(600)

    execfile('/home/spt3g/pydfmux/users/anluser/anl_master_script.py')

#    if 'good_bolos' in locals():
#    	overbias_results = good_bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)
#    else:	
#    	overbias_results = bolos.overbias_and_null(cold_overbias=False, serialize=True,carrier_amplitude=0.0135, scale_by_frequency=True)


zero_everything()

print waferstarttemps
print measurestarttimes
print waferstoptemps
print measurestoptimes

zero_everything()
