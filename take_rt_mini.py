import anl_fridge_control.serial_connections as sc
import he10_fridge_control.control.gettemp as gt
import pydfmux
import time
import datetime
import subprocess


PID_high_temp = 0.650
PID_low_temp = 0.400
sleeptime = 60

logfile = '/home/spt3g/he10_logs/20170302_again_read.h5'

ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
R_data_path_0137 = '/home/spt3g/output/20170316/rt0137.nc'
R_data_path_0135 = '/home/spt3g/output/20170315/rt0135.nc'

hwm_0137 = '/home/spt3g/hardware_maps/hwm_anl_20170306_W169_and_Rboards/hwm_0137.yml'
hwm_0135 = '/home/spt3g/hardware_maps/hwm_anl_20170306_W169_and_Rboards/hwm_0135.yml'

sc.ChaseLS.set_heater_range(2)
sc.ChaseLS.set_PID_temp(1, PID_high_temp)

while float(gt.gettemp(logfile, 'UC Head'))<0.650:
while float(gt.gettemp(logfile, 'UC Head'))<PID_low_temp:
	print "UC Head temp is " + str(gt.gettemp(logfile, 'UC Head'))
	time.sleep(10)

print "start time: " + str(time.time())

proc_ledgerman_0137 = subprocess.Popen(['python', ledgerman_path, hwm_0137, R_data_path_0137, '-s'])
proc_ledgerman_0135 = subprocess.Popen(['python', ledgerman_path, hwm_0135, R_data_path_0135, '-s'])

settemp = PID_high_temp

while settemp > PID_low_temp:
    sc.ChaseLS.set_PID_temp(1, settemp)
    time.sleep(sleeptime)
    settemp -= 0.010

while float(gt.gettemp(logfile, 'UC Head'))>0.420:
	time.sleep(10)

sc.ChaseLS.set_PID_temp(1, 0.000)
time.sleep(1)
sc.ChaseLS.set_heater_range(0)

while float(gt.gettemp(logfile, 'UC Head'))>0.400:
	time.sleep(10)

#time.sleep(60)

proc_ledgerman_0137.terminate()
proc_ledgerman_0135.terminate()

print "end time: " + str(time.time())

