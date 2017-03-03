# sinusoidal.py
#
# 2016-09-08 LJS
#
# Tells a power supply to set voltages that vary sinusoidally
#
# UPDATE 2016-09-09: Now takes a resistance R to control the
# current.  This is to correct for the current maxing out when
# no current is chosen.  LJS

import anl_fridge_control.powersupply as PS
from math import *

def sinuvolt(driverfile, A, freq, tint, tf, R, y=0, t0=0):
	power=PS.PowerSupply(driverfile)
	t=t0
	while t<tf:
		v=-0.5*A*cos(2*pi*freq*t)+(0.5*A)+y
		name.set_vi(v,v/R)
		time.sleep(tint)
		t=t+tint
	name.set_vi(0,0)
