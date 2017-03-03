
import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt
import anl_fridge_control.serial_connections as sc
import time
import datetime
from anl_fridge_control.basic_functions import finish_cycle


def run():
	'''
	This function runs the first cycle of a cooldown.  Note that it takes more than
	24 hours to run.
	'''
	# set the power supplies to remote mode
	sc.He4p.remote_set()
	sc.He3ICp.remote_set()
	sc.He3UCp.remote_set()

	# ask the user for the name of the logfile
	logfile=raw_input('The path to the logfile is: /home/spt3g/')
	logfile=str(logfile)

	# wait for the main plate to cool down enough to start a cycle
	print 'Waiting for Main Plate to be below 3.5 K...'
	while float(gt.gettemp(logfile, 'mainplate'))>3.5:
		time.sleep(600)

	# wait for switches to cool enough to not blow the cycle you are about to start
	print 'Waiting for switches to be below 10 K...'
	while float(gt.gettemp(logfile, 'He3 UC Switch'))>10:
		time.sleep(600)
	while float(gt.gettemp(logfile, 'He3 IC Switch'))>10:
		time.sleep(600)
	while float(gt.gettemp(logfile, 'He4 IC Switch'))>10:
		time.sleep(600)

	# start a cycle
	print 'Starting cycle...'

	# heat up the pumps
	print 'Setting pump voltages.'
	he4v=9.50
	he3icv=6.50
	he3ucv=6.50
	sc.He4p.set_voltage(he4v)
	sc.He3ICp.set_voltage(he3icv)
	sc.He3UCp.set_voltage(he3ucv)

	print 'Waiting for pumps to heat (this will take a long time)'

	try:
		# heat up the pumps at a high voltage to help accelerate the process
		while float(gt.gettemp(logfile, 'He4 IC Pump'))<30.00:
			time.sleep(600)
		he4v=7.50
		sc.He4p.set_voltage(he4v)

		while float(gt.gettemp(logfile, 'He3 UC Pump'))<35.00:
			time.sleep(60)
		he3ucv=5.00
		sc.He3UCp.set_voltage(he3ucv)

		while float(gt.gettemp(logfile, 'He3 IC Pump'))<35.00:
			time.sleep(60)
		he3icv=4.00
		sc.He3ICp.set_voltage(he3icv)

		# wait to help the pump temperatures keep rising to where we want them
		time.sleep(60*60)

		# set stabilizing voltages
		he4v=3.00
		sc.He4p.set_voltage(he4v)
		he3icv=3.20
		sc.He3ICp.set_voltage(he3icv)
		he3ucv=4.60
		sc.He3UCp.set_voltage(he3ucv)

		# wait 2 hours for temperatures to hopefully settle
		time.sleep(2*60*60)

		# wait for UC Head and IC Head to get cold
		while float(gt.gettemp(logfile, 'UC Head'))>4.00:
			# monitor temperatures and adjust voltage if needed
			if float(gt.gettemp(logfile, 'He4 IC Pump'))>42.50 and he4v>2.50:
				he4v-=0.05
				sc.He4p.set_voltage(he4v)
			elif float(gt.gettemp(logfile, 'He4 IC Pump'))<40.00 and he4v<3.50:
				he4v+=0.05
				sc.He4p.set_voltage(he4v)

			if float(gt.gettemp(logfile, 'He3 IC Pump'))>46.00 and he3icv>2.50:
				he3icv-=0.05
				sc.He3ICp.set_voltage(he3icv)
			elif float(gt.gettemp(logfile, 'He3 IC Pump'))<44.00 and he3icv<3.50:
				he3icv+=0.05
				sc.He3ICp.set_voltage(he3icv)

			if float(gt.gettemp(logfile, 'He3 UC Pump'))>46.00 and he3ucv>4.00:
				he3ucv-=0.05
				sc.He3UCp.set_voltage(he3ucv)
			elif float(gt.gettemp(logfile, 'He3 UC Pump'))<44.00 and he3ucv<5.00:
				he3icv=+0.05
				sc.He3UCp.set_voltage(he3ucv)

			print datetime.datetime.now()
			print "He4p: %s\r\nHe3ICp: %s\r\nHe3UCp: %s\r\n" %(he4v, he3icv, he3ucv)
			time.sleep(60*60)

		while float(gt.gettemp(logfile, 'IC Head'))>4.00:
			if float(gt.gettemp(logfile, 'He4 IC Pump'))>42.50 and he4v>2.50:
				he4v-=0.05
				sc.He4p.set_voltage(he4v)
			elif float(gt.gettemp(logfile, 'He4 IC Pump'))<40.00 and he4v<3.50:
				he4v+=0.05
				sc.He4p.set_voltage(he4v)

			if float(gt.gettemp(logfile, 'He3 IC Pump'))>46.00 and he3icv>2.50:
				he3icv-=0.05
				sc.He3ICp.set_voltage(he3icv)
			elif float(gt.gettemp(logfile, 'He3 IC Pump'))<44.00 and he3icv<3.50:
				he3icv+=0.05
				sc.He3ICp.set_voltage(he3icv)

			if float(gt.gettemp(logfile, 'He3 UC Pump'))>46.00 and he3ucv>4.00:
				he3ucv-=0.05
				sc.He3UCp.set_voltage(he3ucv)
			elif float(gt.gettemp(logfile, 'He3 UC Pump'))<44.00 and he3ucv<5.00:
				he3icv=+0.05
				sc.He3UCp.set_voltage(he3ucv)

			print datetime.datetime.now()
			print "He4p: %s\r\nHe3ICp: %s\r\nHe3UCp: %s\r\n" %(he4v, he3icv, he3ucv)
			time.sleep(60*60)

	except:
		# in case of crash, step the voltage down to zero after waiting for a fix
		print datetime.datetime.now()
		print "An error occurred!  Setting all pumps to nominally correct voltages for 12 hours."
		print "Will begin stepping down voltages after 12 hours of waiting."

		sc.He4p.set_voltage(3.00)
		sc.He3ICp.set_voltage(3.20)
		sc.He3UCp.set_voltage(4.60)
		errortime=0
		while errortime<(12*60*60):
			time.sleep(60*60)
			errortime+=1
			print "INTERVENTION NEEDED! Waited %s of 12 hours so far." %(errortime)

		print datetime.datetime.now()
		print "Setting all pumps to 1.5 V for 3 hours."

		sc.He4p.set_voltage(1.50)
		sc.He3ICp.set_voltage(1.50)
		sc.He3UCp.set_voltage(1.50)
		errortime=0
		while errortime<(3*60*60):
			time.sleep(60*60)
			errortime+=1
			print "INTERVENTION NEEDED! Waited %s of 3 hours so far." %(errortime)

		print "Setting all pumps to 0 V."

		sc.He4p.set_voltage(0.00)
		sc.He3ICp.set_voltage(0.00)
		sc.He3UCp.set_voltage(0.00)

		print "Voltages stepped down to zero and cycle stopped.  Please do something."
		print datetime.datetime.now()
		quit()

	# heat up the He4 pump to help with condensing
	print "Ramping He4 Pump up to 44 K."
	he4v=5.00
	sc.He4p.set_voltage(he4v)
	while float(gt.gettemp(logfile, 'He4 IC Pump'))<44.00:
		time.sleep(10*60)

	# sleeping at (semi-)stable temperature to allow for condensing
	print "Waiting 1 hour for He-4 to condense."
	condense_time=0
	while condense_time<60:
		time.sleep(10*60)
		if float(gt.gettemp(logfile, 'He4 IC Pump'))<43.00 and he4v<5.50:
			he4v+=0.10
			sc.He4p.set_voltage(he4v)
		else:
			pass
		condense_time+=10
		print "Time elapsed: %s minutes" %(condense_time)

	# turning off He4 pump and turning on switch
	print "Turning off the He4 Pump."
	sc.He4p.set_voltage(0.00)
	time.sleep(2)
	print "Turning on the He4 Switch to 4 V."
	sc.He4s.set_voltage(4.00)

	# heat the He3 pumps to help with condensing
	print "Ramping He3 IC Pump to 54 K and He3 UC Pump to 51 K."
	he3icv=5.20
	sc.He3ICp.set_voltage(he3icv)
	he3ucv=5.80
	sc.He3UCp.set_voltage(he3ucv)
	while (float(gt.gettemp(logfile, 'He3 UC Pump'))<51.00 and float(gt.gettemp(logfile, 'He3 IC Pump'))<54.00):
		time.sleep(60*60)
	while (float(gt.gettemp(logfile, 'He3 UC Pump'))<51.00 or float(gt.gettemp(logfile, 'He3 IC Pump'))<54.00):
		if float(gt.gettemp(logfile, 'He3 UC Pump'))>52.00:
			he3ucv-=0.20
			sc.He3UCp.set_voltage(he3ucv)
		if float(gt.gettemp(logfile, 'He3 IC Pump'))>55.00:
			he3icv-=0.20
			sc.He3ICp.set_voltage(he3icv)
		time.sleep(60*60)

	# wait for HEX to rise, turn off pumps, turn on switches
	finish_cycle(logfile)

if __name__=='__main__':
	run()
