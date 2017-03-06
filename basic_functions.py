# basic_functions.py
#
# Automated codes to start things at the beginning of the day, run an automatic
# fridge cycle, and turn all power supplies and heaters to zero volts.
#
# LJS 2016-10-14

#from matplotlib.pylab import switch_backend
#switch_backend('Agg')
import serial
import pydfmux
import os,time
import datetime
import numpy as np
from pydfmux.core.utils.conv_functs import build_hwm_query
#from matplotlib.pylab import switch_backend
#switch_backend('Agg')

import os,time
import sys
sys.path.append('/home/spt3g/')

import he10_fridge_control.control.gettemp as gt

import numpy as np
import anl_fridge_control.serial_connections as sc

###############################################################################
############## Edit this first part to do what you want it to do ##############
###############################################################################

# Choose a hardware map and IceBoard

hwm_dir='/home/spt3g/hardware_maps/hwm_anl_20170201_Nb_and_Al/hwm_anl_complete.yml'
board='0135'

hwm=pydfmux.load_session(open(hwm_dir))['hardware_map']
ds=hwm.query(pydfmux.Dfmux)
sqcbs=hwm.query(pydfmux.SQUIDController)
squids=hwm.query(pydfmux.SQUID)
bolos = hwm.query(pydfmux.Bolometer)
rm=hwm.query(pydfmux.ReadoutModule)
d=ds[0]

# Choose which modules to use when overbiasing/dropping bolometers

gbolos=[]
for bb in bolos.all():
    if (bb.iceboard != None) and (bb.iceboard.serial !=None):
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==2):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==3):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==4):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==1):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==2):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==3):
            gbolos.append(bb)
        if bb.iceboard.serial==board and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==4):
            gbolos.append(bb)


###############################################################################
##### Items below do not need to be changed after setting for your fridge #####
###############################################################################

def start_of_day(logfile, set_squid_feedback=False, set_gain=False):
	'''
	Starts things for you by heating the UC head (using PID and pump), initializing the board, tuning squids, and taking a rawdump.
	'''
	# set voltages to 0, let the switches cool
	print 'Setting the switches to zero to cool.'
	sc.He3ICp.remote_set()
	sc.He3UCp.remote_set()

	sc.He3ICp.set_voltage(0)
	sc.He3ICs.set_voltage(0)
	sc.He3UCp.set_voltage(0)
	sc.He3UCs.set_voltage(0)

	gt.gettemp(logfile, 'He3 IC Switch'); gt.gettemp(logfile, 'He3 UC Switch')
	while float(gt.gettemp(logfile, 'He3 UC Switch'))>1:
		while float(gt.gettemp(logfile, 'He3 IC Switch'))>1:
			gt.gettemp(logfile, 'He3 UC Switch'); gt.gettemp(logfile, 'He3 IC Switch')
			time.sleep(10)

	# set UC pump voltage and start the heater to get above Tc
	print 'Setting ultra pump to 3.00 V.'
	sc.He3UCp.set_voltage(3.00)
	time.sleep(60)
	print 'Setting the heater to 500 mK at 1.5 mW.'
	sc.ChaseLS.set_PID_temp(1,0.500)
	time.sleep(1)
	sc.ChaseLS.set_heater_range(2)
	time.sleep(1)
	gt.gettemp(logfile, 'UC Head')
	while float(gt.gettemp(logfile, 'UC Head'))<0.500:
		time.sleep(20)
		gt.gettemp(logfile, 'UC Head')
	time.sleep(1)
	print 'Setting the heater to 650 mK at 15 mW.'
	sc.ChaseLS.set_PID_temp(1, 0.650)
	time.sleep(1)
	sc.ChaseLS.set_heater_range(3)
	time.sleep(1)

	print 'Setting the ultra pump to 1.50 V'
	sc.He3UCp.set_voltage(1.00)
	while float(gt.gettemp(logfile, 'UC Head'))<0.650:
		time.sleep(20)
		gt.gettemp(logfile, 'UC Head')

	sc.He3UCp.set_voltage(1.50)
	print 'Waiting...'
	time.sleep(300)

	# initialize the board
	print 'Initializing the board.'
	try:
		ds.initialize_iceboard(use_test_IRIG=True)
		sqcbs.initialize_squidcontroller()
		time.sleep(5)
		ds.set_fir_stage(6)
		ds.align_sampling()
	except URLError:
		print 'Could not initialize because the power is not on!  Waiting...'
		initboard = raw_input("Type 'done' when the power is set to 17 V.    ")
		if initboard == 'done':
			ds.initialize_iceboard(use_test_IRIG=True)
			sqcbs.initialize_squidcontroller()
			time.sleep(5)
			ds.set_fir_stage(6)
			ds.align_sampling()

	# zero combs
	ds.clear_all()
	ds.clear_dan()

	# heat the squids
	print 'Heating SQUIDs.'
	sqcbs.heat_squids(heat_time_sec=15,heat_voltage=4.0,wait_time_sec=1200)

	# tune the squids
	print 'Tuning SQUIDs.'
	sq_results=squids.tune_squid(squid_bias_reference=[1.6],squid_bias_start=0.8,flux_start=0,flux_stop=2.0,minap2p=0.05)

	# squid feedback (optional)
	if set_squid_feedback:
		print 'Setting SQUID feedback.'
		for squid in squids.all():
			squid.module.set_squid_feedback('SQUID_LOWPASS')

	# set gain (optional)
	if set_gain:
		print 'Setting gain.'
		rm.set_mezzanine_gain(15,'CARRIER')
		rm.set_mezzanine_gain(15,'NULLER')

	# take a rawdump
	print 'Taking a rawdump.'
	results=rm.take_rawdump(num_samples=50000)

	print 'Startup is complete.  Start whatever you want to do today!'


def zero_everything():
	'''
	Sets UC and IC voltages on pumps and switches to 0, sets the heater temperature and range to 0.  A good safety measure for not accidentally blowing the cycle.
	'''
	sc.He3ICp.set_voltage(0.00)
	sc.He3UCp.set_voltage(0.00)
	time.sleep(1)
	sc.He3ICs.set_voltage(0.00)
	sc.He3UCs.set_voltage(0.00)
	time.sleep(1)
	sc.He4p.set_voltage(0.00)
	sc.He4s.set_voltage(0.00)
	sc.ChaseLS.set_PID_temp(1,0.000)
	time.sleep(1)
	sc.ChaseLS.set_heater_range(0)

def finish_cycle(hex_filename):
	print 'Beginning the hex_watcher_3000 program to finish the cycle.'
	print gt.gettemp(hex_filename,'HEX')
	while float(gt.gettemp(hex_filename,'HEX'))<1.06:
		time.sleep(60)
		print datetime.datetime.now()
		print gt.gettemp(hex_filename,'HEX')
	time.sleep(60)

	print 'Turning off inter pump and ultra pump.'
	print datetime.datetime.now()

	sc.He3ICp.set_voltage(0.00)
	sc.He3UCp.set_voltage(0.00)

	time.sleep(60)

	print 'Turning on inter switch.'
	print datetime.datetime.now()
	sc.He3ICs.set_voltage(4.00)
	time.sleep(240)

	print 'Turning on ultra switch.'
	print datetime.datetime.now()
	sc.He3UCs.set_voltage(3.00)

	print 'Waiting one hour for cooling...'
	print datetime.datetime.now()

	time.sleep(3600)

	print 'Cycle is complete!'
	print datetime.datetime.now()

def autocycle(logfile, start=False):
	'''
	This is a function to run a fridge cycle.  Note that it takes 6+ hours to run.
	'''
	try:
		print "Turning off mezzanines."
		ds.set_mezzanine_power(False,1)
		ds.set_mezzanine_power(False,2)
		time.sleep(60)

		print "Mezzanines off, ready to go."

		sc.He4p.remote_set()
		sc.He3ICp.remote_set()
		sc.He3UCp.remote_set()

		print 'Setting the heater, switches, and pumps to 0.'

		zero_everything()

		print 'Waiting for switches to cool.'

		while float(gt.gettemp(logfile, 'He3 IC Switch'))>2.00:
			time.sleep(10)
		while float(gt.gettemp(logfile, 'He3 UC Switch'))>2.00:
			time.sleep(10)
		while float(gt.gettemp(logfile, 'He4 IC Switch'))>4.00:
			time.sleep(10)
		print 'Switches are cool, beginning heating.'

		print ''

		print 'Turning He4 pump to 12.00 V.'
		sc.He4p.set_voltage(12.00)

		print 'Turning inter pump to 9.60 V.'
		sc.He3ICp.set_voltage(9.60)

		print 'Turning ultra pump to 6.30 V.'
		sc.He3UCp.set_voltage(6.30)

		print ''

		print 'Waiting 30 minutes for pumps to heat.'
		t=0
		while t<1800:
			time.sleep(60)
			t=t+60
			minutes=str(t/60)
			print ('%s minutes elapsed so far.' % minutes)

		print 'Turning He4 pump to 9.50 V.'
		sc.He4p.set_voltage(9.50)

		print 'Turning IC pump to 5.10 V.'
		sc.He3ICp.set_voltage(5.10)

		print 'Turning UC pump to 5.30 V.'
		sc.He3UCp.set_voltage(5.30)

		print 'Waiting 20 minutes.'
		t=0
		while t<1200:
			time.sleep(60)
			t=t+60
			minutes=str(t/60)
			print ('%s minutes elapsed so far.' % minutes)

		print 'Turning He4 pump to 5.0 V.'
		sc.He4p.set_voltage(5.0)

		print 'Waiting for He4 pump temperature to reach 43 K.'
		while float(gt.gettemp(logfile, 'He4 IC Pump'))<43:
			time.sleep(10)

		print 'Turning He4 pump to 3.0 V.'
		sc.He4p.set_voltage(3.00)

		print 'Waiting 5 minutes.'
		time.sleep(300)

		print 'Setting He4 pump to 0.0 V.'
		sc.He4p.set_voltage(0.00)

		print 'Sleeping for 3 minutes.'
		time.sleep(180)

		print 'Setting He4 switch to 4.00 V.'
		sc.He4s.set_voltage(4.00)

		print 'Waiting for He3 IC Pump temperatures to change.'
		while float(gt.gettemp(logfile, 'He3 IC Pump'))<52:
			time.sleep(10)

		print 'Setting inter pump to 3.0 V.'
		sc.He3ICp.set_voltage(3.00)

		print 'Waiting for He3 UC Pump temperature to change.'
		while float(gt.gettemp(logfile, 'He3 UC Pump'))<52:
			time.sleep(10)

		print 'Setting ultra pump to 5.00 V.'
		sc.He3UCp.set_voltage(5.00)

		finish_cycle(logfile)

		if start==True:
			start_of_day()
		else:
			print 'Cycle is complete.'
			return

	except:
		print 'Crashed!'
		print datetime.datetime.now()
		zero_everything()

#def first_cycle():
	# set the power supplies to remote mode
#	He4p.remote_set()
#	He3ICp.remote_set()
#	He3UCp.remote_set()

	# wait for the main plate to cool down enough to start a cycle
#	print 'Waiting for Main Plate to be below 3.5 K...'
#	get_monitor_temp()
#	while float(get_monitor_temp()['Main Plate'])>3.5:
#		time.sleep(600)
#		get_monitor_temp()

	# wait for switches to cool enough to not blow the cycle you are about to start
#	print 'Waiting for switches to be below 10 K...'
#	while float(get_monitor_temp()['Ultra Switch'])>10:
#		time.sleep(600)
#		get_monitor_temp()
#	while float(get_monitor_temp()['Inter Switch'])>10:
#		time.sleep(600)
#		get_monitor_temp()
#	while float(get_monitor_temp()['He4 Switch'])>10:
#		time.sleep(600)
#		get_monitor_temp()
#
#	# start a cycle
#	print 'Starting cycle...'
#
#	# heat up the pumps
#	print 'Ramping up pumps (this will take awhile)...'
#	he4v=9.50
#	he3icv=6.50
#	he3ucv=6.50
#	He4p.set_voltage(he4v)
#	He3ICp.set_voltage(he3icv)
#	He3UCp.set_voltage(he3ucv)
#
#	# wait a really long time (we want ultra head and inter head to be cold)
#	print 'Waiting 19 hours.  See you tomorrow! (Please monitor every few hours)'
#	starttime=time.time()
#	starttime
#	nowtime=0
#
#	# first half of the 19 hours
#	try:
#		while float(get_monitor_temp()['He4 Pump'])<30.00:
#			time.sleep(60)
#			nowtime=time.time()-starttime
#			get_monitor_temp()
#		he4v=7.50
#		He4p.set_voltage(he4v)
#		while float(get_monitor_temp()['Ultra Pump'])<35.00:
#			time.sleep(60)
#			nowtime=time.time()-starttime
#			get_monitor_temp()
#		he3ucv=5.00
#		He3UCp.set_voltage(he3ucv)
#		while float(get_monitor_temp()['Inter Pump'])<35.00:
#			time.sleep(60)
#			nowtime=time.time()-starttime
#			get_monitor_temp()
#		he3icv=4.00
#		He3ICp.set_voltage(he3icv)
#	except ValueError:
#		time.sleep(60)
#		nowtime=time.time()-starttime
#		try:
#			while float(get_monitor_temp()['He4 Pump'])<30.00:
#				time.sleep(60)
#				nowtime=time.time()-starttime
#				get_monitor_temp()
#			he4v=7.50
#			He4p.set_voltage(he4v)
#			while float(get_monitor_temp()['Ultra Pump'])<35.00:
#				time.sleep(60)
#				nowtime=time.time()-starttime
#				get_monitor_temp()
#			he3ucv=5.00
#			He3UCp.set_voltage(he3ucv)
#			while float(get_monitor_temp()['Inter Pump'])<35.00:
#				time.sleep(60)
#				nowtime=time.time()-starttime
#				get_monitor_temp()
#			he3icv=4.00
#			He3ICp.set_voltage(he3icv)
#		except ValueError:
##				fp=open('/home/spt3g/he10_fridge_control/Lauren/error_text.txt','rb')
##				msg = MIMEText(fp.read())
##				fp.close()
##
##				me = 'lausaunders@gmail.com'
#				msg['Subject'] = 'An urgent message from your cryostat'
#				msg['From'] = me
#				msg['To'] = me
#
#				s = smtplib.SMTP('localhost')
#				s.sendmail(me, me, msg.as_string())
#				s.quit()
#			he4pset=3.00
#			he3icpset=3.00
#			he3ucpset=4.50
#			while he3ucpset>0.10:
#				he3icpset=he3icpset-0.20
#				he4pset=he4pset-0.20
#				if he3icpset>0.00:
#					He3ICp.set_voltage(he3icpset)
#				if he4pset>0.00:
#					He4p.set_voltage(he4pset)
#				he3ucpset=he3ucpset-0.20
#				He3UCp.set_voltage(he3ucpset)
#				time.sleep(300)
#			He3UCp.set_voltage(0.00)
#			He3ICp.set_voltage(0.00)
#			He4p.set_voltage(0.00)
#			return
#
#	time.sleep(60)
#	nowtime=time.time()-starttime
#	while he4v>3.0:
#		he4v=he4v-0.5
#		time.sleep(120)
#		nowtime=time.time()-starttime
#	while he3ucv>4.60:
#		he3ucv=he3ucv-0.20
#		time.sleep(120)
#		nowtime=time.time()-starttime
#	while he3icv>3.20:
#		he3icv=he3icv-0.20
#		time.sleep(120)
#		nowtime=time.time()-starttime
#	time.sleep(120)
#	nowtime=time.time()-starttime

#	while nowtime<68400:
#		get_monitor_temp()
#		if float(get_monitor_temp()['He4 Pump'])<40.00 and 2.90<=he4v<3.30:
#			he4v=he4v+0.05
#			He4p.set_voltage(he4v)
#		elif float(get_monitor_temp()['He4 Pump']>42.50 and 3.30>=he4v>2.90:
#			he4v=he4v-0.05
#			He4P.set_voltage(he4v)
#		if float(get_monitor_temp()['Inter Pump'])<44.00 and 2.90<=he3icv<3.30:
#			he3icv=he3icv+0.05
#			He3ICp.set_voltage(he3icv)
#		elif float(get_monitor_temp()['Inter Pump'])>46.00 and 3.30>=he3icv>2.90:
#			he3icv=he3icv-0.05
#			He3ICp.set_voltage(he3icv)
#		if float(get_monitor_temp()['Ultra Pump'])<44.00 and 4.70>he3ucv>=4.40:
#			he3ucv=he3ucv+0.05
#			He3UCp.set_voltage(he3ucv)
#		elif float(get_monitor_temp()['Ultra Pump'])>46.00 and 4.70>=he3ucv>4.40:
#			he3ucv=he3ucv-0.05
#			He3UCp.set_voltage(he3ucv)
#
#		time.sleep(300)
#		nowtime=time.time()-starttime





#		if float(get_monitor_temp()['He4 Pump'])>41.50:
#			if float(He4p.read_voltage())>0.50:
#				he4v=he4v-0.50
#				He4p.set_voltage(he4v)
#			else:
#				pass
#		elif float(get_monitor_temp()['He4 Pump'])<40.50:
#			he4v=he4v+0.10
#			He4p.set_voltage(he4v)
#		if float(get_monitor_temp()['Inter Pump'])>45.50:
#			if float(He3ICp.read_voltage())>0.50:
#				he3icv=he3icv-0.50
#				He3ICp.set_voltage(he3icv)
#			else:
#				pass
#		elif float(get_monitor_temp()['Inter Pump'])<44.50:
#			if float(get_monitor_temp()['Inter Pump'])==0.00:
#				zero_everything()
#				print 'Crashed!'
#				return
#			else:
#				he3icv=he3icv+0.10
#				He3ICp.set_voltage(he3icv)
#		if float(get_monitor_temp()['Ultra Pump'])>45.50:
#			if float(He3UCp.read_voltage())>0.50:
#				he3ucv=he3ucv-0.50
#				He3UCp.set_voltage(he3ucv)
#			else:
#				pass
#		elif float(get_monitor_temp()['Ultra Pump'])<44.50:
#			if float(get_monitor_temp()['Ultra Pump'])==0.00:
#				zero_everything()
#				print 'Crashed!'
#				return
#			else:
#				he3ucv=he3ucv+0.10
#				He3UCp.set_voltage(he3ucv)
#		sleepytime=sleepytime+60
#
#	# second half of the 19 hours
#	while sleepytime<68400:
#		time.sleep(60)
#		get_monitor_temp()
#		print get_monitor_temp()
#		if float(get_monitor_temp()['He4 Pump'])>41.00:
#			if float(He4p.read_voltage())>0.20:
#				he4v=he4v-0.20
#				He4p.set_voltage(he4v)
#			else:
#				pass
#		elif float(get_monitor_temp()['He4 Pump'])<39.50:
#			if float(get_monitor_temp()['He4 Pump'])==0.00:
#				zero_everything()
#				print 'Crashed!'
#				return
#			else:
#				he4v=he4v+0.10
#				He4p.set_voltage(he4v)
#		if float(get_monitor_temp()['Inter Pump'])>45.50:
#			if float(He3ICp.read_voltage())>0.20:
#				he3icv=he3icv-0.20
#				He3ICp.set_voltage(he3icv)
#			else:
#				pass
#		elif float(get_monitor_temp()['Inter Pump'])<44.50:
#			if float(get_monitor_temp()['Inter Pump'])==0.00:
#				zero_everything()
#				print 'Crashed!'
#				return
#			else:
#				he3icv=he3icv+0.10
#				He3ICp.set_voltage(he3icv)
#		if float(get_monitor_temp()['Ultra Pump'])>45.50:
#			if float(He3UCp.read_voltage())>0.20:
#				he3ucv=he3ucv-0.20
#				He3UCp.set_voltage(he3ucv)
#			else:
#				pass
#		elif float(get_monitor_temp()['Ultra Pump'])<44.50:
#			if float(get_monitor_temp()['Ultra Pump'])==0.00:
#				zero_everything()
#				print 'Crashed!'
#				return
#			else:
#				he3ucv=he3ucv+0.10
#				He3UCp.set_voltage(he3ucv)
#		sleepytime=sleepytime+60
#
#	# check every 20 minutes to see if ultra and inter heads are cool enough
#	print 'Waiting for Ultra Head and Inter Head to be below 4 K...'
#	while float(ChaseLS.get_temps()['A'])>4.0:
#		time.sleep(20*60)
#		ChaseLS.get_temps()
#	while float(ChaseLS.get_temps()['B'])>4.0:
#		time.sleep(20*60)
#		ChaseLS.get_temps()
#
#	print 'Ramping Helium-4 pump up to 44 K...'
#	he4v=he4v+2.00
#	He4p.set_voltage(he4v)
#	while float(get_monitor_temp()['He4 Pump'])<44.00:
#		time.sleep(60)
#		get_monitor_temp()
#
#	print 'Waiting 1 hour for Helium-4 to condense...'
#	condense_time=0
#	while condense_time<3600:
#		time.sleep(10)
#		get_monitor_temp()
#		if float(get_monitor_temp()['He4 Pump'])>44.00:
#			he4v=he4v-0.20
#			He4p.set_voltage(he4v)
#		elif float(get_monitor_temp()['He4 Pump'])<43.00:
#			he4v=he4v+0.10
#			He4p.set_voltage(he4v)
#		condense_time = condense_time + 10
#
#	print 'Turning off the Helium-4 pump.'
#	He4p.set_voltage(0.00)
#	time.sleep(1)
#
#	print 'Turning on the Helium-4 switch.'
#	He4s.set_voltage(4.00)
#
#	print 'Ramping Inter Pump to 54 K and Ultra Pump to 51 K...'
#	he3icv = he3icv + 0.50; he3ucv = he3ucv + 0.50
#	He3ICp.set_voltage(he3icv)
#	He3UCp.set_voltage(he3ucv)
#	while float(get_monitor_temp()['Inter Pump'])<54.00:
#		time.sleep(20)
#		get_monitor_temp()
#	while float(get_monitor_temp()['Ultra Pump'])<51.00:
#		time.sleep(20)
#		get_monitor_temp()
#
#	print 'Waiting for heat exchanger to heat slightly...'
#	while float(get_monitor_temp()['Heat Exchanger'])<1.06:
#		time.sleep(20)
#		get_monitor_temp()
#	while float(get_monitor_temp()['He4 Pump'])>3.80:
#		time.sleep(20)
#		get_monitor_temp()
#
#	print 'Turning off Inter Pump and Ultra Pump.'
#	He3UCp.set_voltage(0.00)
#	He3ICp.set_voltage(0.00)
#	time.sleep(1)
#
#	print 'Turning on Inter Switch.'
#	He3ICs.set_voltage(4.00)
#	time.sleep(60*4)

#	print 'Turning on Ultra Switch.'
#	He3UCs.set_voltage(3.00)
#
#	print 'Waiting one hour for cooling...'
#	time.sleep(3600)
#
#	print 'Cycle is complete!'
