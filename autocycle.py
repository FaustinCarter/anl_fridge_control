import serial
import pydfmux
import os,time

import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt

import anl_fridge_control.serial_connections as sc



def autocycle():
	'''
	This is a function to run a fridge cycle.  Note that it takes 6+ hours to run.
	'''
	try:
		logfile=raw_input('What is the logfile?  /home/spt3g/')
		logfile=str(logfile)

		hwm_dir=raw_input('What is the full path to the hardware map yml?  ')
		hwm_dir=str(hwm_dir)

		hwm=pydfmux.load_session(open(hwm_dir))['hardware_map']
		ds=hwm.query(pydfmux.Dfmux)
		d=ds[0]

		print "Turning off mezzanines."
		ds.set_mezzanine_power(False,1)
		ds.set_mezzanine_power(False,2)
		time.sleep(60)

		raw_input('Please press enter if the mezzanines are actually off (for testing).')
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

		print 'Cycle is complete.'
		return

	except:
		print 'Crashed!'
		print datetime.datetime.now()
		zero_everything()

if __name__=='__main__':
	autocycle()
