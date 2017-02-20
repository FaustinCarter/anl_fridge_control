import pydfmux
import matplotlib.pyplot as plt
import os,time
import numpy as pn
from pydfmux.core.utils.conv_functs import build_hwm_query
import pickle,pdb
import scipy as sp
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF
from pydfmux.core.utils.transferfunctions import convert_adc_samples

#calibration factor
cfp=convert_TF(15, 'carrier',unit='RAW')#*1e9

#give the filenames
rt_raw_data='/home/spt3g/ledgerman_output/20161209/down1.nc'
hwm_dir='/home/spt3g/hardware_maps/hwm_anl_20161207_w132/hwm_anl_complete.yml'
temp_data='/home/spt3g/ledgerman_output/20161209/temps_down1.pkl'
overbias_data='/home/spt3g/output/20161209/20161209_201700_overbias_and_null'
iceboard='0135'

#function to read in the data from a .nc file
def read_netcdf_fast(filename,cal_factor_pa=cfp):

    data=Dataset(filename,'r',format='NETCDF4')
    datavars=[var.rstrip('_I') for var in data.variables if '_I' in var]

    ixs = np.arange(len(data.variables['Time']), step=215)

    time_sec=data.variables['Time'][ixs]
    time_sec=time_sec-time_sec[0]

    data_i={}
    data_q={}
    for var in datavars:
        i_comp=data.variables[var+'_I'][ixs]
        q_comp=data.variables[var+'_Q'][ixs]
        if 'L' not in var:
            data_i[var]=i_comp*cal_factor_pa
            data_q[var]=q_comp*cal_factor_pa
        else:
            data_i[var]=i_comp
            data_q[var]=q_comp
    return data_i,data_q,time_sec

#read in data
dat=read_netcdf_fast(rt_raw_data)

#separate dat into i and q channels, make time a separate variable
dat_i=dat[0]
dat_q=dat[1]
ts=dat[2]

# get temperature data
temperatures=pickle.load(open(temp_data,'r'))

temps=[]
for i in range(len(temperatures)):
	temps.append(float(temperatures[i]))
print "The length of temps is " + str(len(temps))

# get voltages from the overbias files
# mezz 1 mod 1
#obd11=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_1.ReadoutModule_1_OUTPUT.pkl','r'))
#voltages_11=[]
#for jj in range(len(obd11['overbiased'])):
#	voltages_11.append(obd11['overbiased'][jj+1]['V'])
#for kk in j11:
#	voltages_11.remove(voltages_11[kk])
#print "The length of voltages_11 is " + str(len(voltages_11))
#v11=len(voltages_11)

#mezz 1 mod 2
obd12=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_1.ReadoutModule_2_OUTPUT.pkl','r'))
voltages_12=[]
for jj in obd12['overbiased']:
	voltages_12.append(obd12['overbiased'][jj]['V'])
#for kk in j12:
#	voltages_12.remove(voltages_12[kk])
print "The length of voltages_12 is " + str(len(voltages_12))
v12=len(voltages_12)

# mezz 1 mod 3
obd13=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_1.ReadoutModule_3_OUTPUT.pkl','r'))
voltages_13=[]
for jj in obd13['overbiased']:
	voltages_13.append(obd13['overbiased'][jj]['V'])
#for kk in j13:
#	voltages_13.remove(voltages_13[kk])
print "The length of voltages_13 is " + str(len(voltages_13))
v13=len(voltages_13)

# mezz 1 mod 4
obd14=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_1.ReadoutModule_4_OUTPUT.pkl','r'))
voltages_14=[]
for jj in obd14['overbiased']:
	voltages_14.append(obd14['overbiased'][jj]['V'])
#for kk in j14:
#	voltages_14.remove(voltages_14[kk])
print "The length of voltages_14 is " + str(len(voltages_14))
v14=len(voltages_14)

# mezz 2 mod 1
obd21=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_2.ReadoutModule_1_OUTPUT.pkl','r'))
voltages_21=[]
for jj in obd21['overbiased']:
	voltages_21.append(obd21['overbiased'][jj]['V'])
#for kk in j21:
#	voltages_21.remove(voltages_21[kk])
print "The length of voltages_21 is " + str(len(voltages_21))
v21=len(voltages_21)

# mezz 2 mod 2
obd22=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_2.ReadoutModule_2_OUTPUT.pkl','r'))
voltages_22=[]
for jj in obd22['overbiased']:
	voltages_22.append(obd22['overbiased'][jj]['V'])
#for kk in j22:
#	voltages_22.remove(voltages_22[kk])
print "The length of voltages_22 is " + str(len(voltages_22))
v22=len(voltages_22)

# mezz 2 mod 3
obd23=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_2.ReadoutModule_3_OUTPUT.pkl','r'))
voltages_23=[]
for jj in obd23['overbiased']:
	voltages_23.append(obd23['overbiased'][jj]['V'])
#for kk in j23:
#	voltages_23.remove(voltages_23[kk])
print "The length of voltages_23 is " + str(len(voltages_23))
v23=len(voltages_23)

# mezz 2 mod 4
obd24=pickle.load(open(overbias_data + '/data/IceBoard_'+str(iceboard)+'.Mezz_2.ReadoutModule_4_OUTPUT.pkl','r'))
voltages_24=[]
for jj in obd24['overbiased']:
	voltages_24.append(obd24['overbiased'][jj]['V'])
#for kk in j24:
#	voltages_24.remove(voltages_24[kk])
print "The length of voltages_24 is " + str(len(voltages_24))
v24=len(voltages_24)

#hardware map
hwm=pydfmux.load_session(open(hwm_dir))['hardware_map']
ds=hwm.query(pydfmux.Dfmux)
sqcbs=hwm.query(pydfmux.SQUIDController)
squids=hwm.query(pydfmux.SQUID)
bolos = hwm.query(pydfmux.Bolometer)
rm=hwm.query(pydfmux.ReadoutModule)
d=ds[0]

#m1m1_init=[]
m1m2_init=[]
m1m3_init=[]
m1m4_init=[]
m2m1_init=[]
m2m2_init=[]
m2m3_init=[]
m2m4_init=[]

#make a list of all bolometers on each module that, in the correct format
for bb in bolos.all():
	if (bb.iceboard != None) and (bb.iceboard.serial != None):
#		if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==2):
#			q=str(bb)
#			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
#			y=unicode('w109_')+unicode(z)
#			m1m2_init.append(y)
#        	if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==3):
#			q=str(bb)
#			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
#			y=unicode('w109_')+unicode(z)
#			m1m3_init.append(y)
#        	if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==1 and (bb.readout_channel.module.module==4):
#			q=str(bb)
#			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
#			y=unicode('w109_')+unicode(z)
#			m1m4_init.append(y)
        	if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==1):
			q=str(bb)
			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
			y=unicode('w132_')+unicode(z)
			m2m1_init.append(y)
        	if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==2):
			q=str(bb)
			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
			y=unicode('w132_')+unicode(z)
			m2m2_init.append(y)
        	if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==3):
			q=str(bb)
			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
			y=unicode('w132_')+unicode(z)
			m2m3_init.append(y)
#		if bb.iceboard.serial=='0135' and bb.readout_channel.mezzanine.mezzanine==2 and (bb.readout_channel.module.module==4):
#			q=str(bb)
#			z=q.split('.Bolometer')[1].split("u'")[1].split("')")[0]
#			y=unicode('w109_')+unicode(z)
#			m2m4_init.append(y)

#m1m1=[]
#m1m1_nope=[]
#j11=[]
m1m2=[]
m1m2_nope=[]
j12=[]
m1m3=[]
m1m3_nope=[]
j13=[]
m1m4=[]
m1m4_nope=[]
j14=[]
m2m1=[]
m2m1_nope=[]
j21=[]
m2m2=[]
m2m2_nope=[]
j22=[]
m2m3=[]
m2m3_nope=[]
j23=[]
m2m4=[]
m2m4_nope=[]
j24=[]

#separate out good bolometers and bad bolometers
#for j in m1m1_init:
#	if dat_i[j][len(dat_1[j])-2]<-10000:
#		m1m1_nope.append(j)
#		j11.append(m1m1_init.index(j))
#	elif dat_i[j][len(dat_i[j])-2]>10000:
#		m1m1_nope.append(j)
#		j11.append(m1m1_init.index(j))
#	else:
#		m1m1.append(j)
# m1m2
if len(m1m2_init)!=len(voltages_12):
	for k in obd12['overbiased']:
		for j in range(len(m1m2_init)):
			if j==(k-1):
				m1m2.append(m1m2_init[j])
	for l in m1m2_init:
		if l not in m1m2:
			m1m2_nope.append('No voltage: ' + str(l))
elif len(m1m2_init)==len(voltages_12):
	for j in m1m2_init:
		m1m2.append(j)
m1m3
if len(m1m3_init)!=len(voltages_13):
	for k in obd13['overbiased']:
		for j in range(len(m1m3_init)):
			if j==(k-1):
				m1m3.append(m1m3_init[j])
	for l in m1m3_init:
		if l not in m1m3:
			m1m3_nope.append('No voltage: ' + str(l))
elif len(m1m3_init)==len(voltages_13):
	for j in m1m3_init:
		m1m3.append(j)
# m1m4
if len(m1m4_init)!=len(voltages_14):
	for k in obd14['overbiased']:
		for j in range(len(m1m4_init)):
			if j==(k-1):
				m1m4.append(m1m4_init[j])
	for l in m1m4_init:
		if l not in m1m4:
			m1m4_nope.append('No voltage: ' + str(l))
elif len(m1m4_init)==len(voltages_14):
	for j in m1m4_init:
		m1m4.append(j)
#m2m1
if len(m2m1_init)!=len(voltages_21):
	for k in obd21['overbiased']:
		for j in range(len(m2m1_init)):
			if j==(k-1):
				m2m1.append(m2m1_init[j])
	for l in m2m1_init:
		if l not in m2m1:
			m2m1_nope.append('No voltage: ' + str(l))
elif len(m2m1_init)==len(voltages_21):
	for j in m2m1_init:
		m2m1.append(j)
#m2m2
if len(m2m2_init)!=len(voltages_22):
	for k in obd22['overbiased']:
		for j in range(len(m2m2_init)):
			if j==(k-1):
				m2m2.append(m2m2_init[j])
	for l in m2m2_init:
		if l not in m2m2:
			m2m2_nope.append('No voltage: ' + str(l))
elif len(m2m2_init)==len(voltages_22):
	for j in m2m2_init:
		m2m2.append(j)
#m2m3
if len(m2m3_init)!=len(voltages_23):
	for k in obd23['overbiased']:
		for j in range(len(m2m3_init)):
			if j==(k-1):
				m2m3.append(m2m3_init[j])
	for l in m2m3_init:
		if l not in m2m3:
			m2m3_nope.append('No voltage: ' + str(l))
elif len(m2m3_init)==len(voltages_23):
	for j in m2m3_init:
		m2m3.append(j)
#m2m4
if len(m2m4_init)!=len(voltages_24):
	for k in obd24['overbiased']:
		for j in range(len(m2m4_init)):
			if j==(k-1):
				m2m4.append(m2m4_init[j])
	for l in m2m4_init:
		if l not in m2m4:
			m2m4_nope.append('No voltage: ' + str(l))
elif len(m2m4_init)==len(voltages_24):
	for j in m2m4_init:
		m2m4.append(j)

# get the data out of a dictionary and into a list
#data2_11=[]
#for i in m1m1:
#	data2_11.append(dat_i[i])
data2_12=[]
for i in m1m2:
	data2_12.append(dat_i[i])
data2_13=[]
for i in m1m3:
	data2_13.append(dat_i[i])
data2_14=[]
for i in m1m4:
	data2_14.append(dat_i[i])
data2_21=[]
for i in m2m1:
	data2_21.append(dat_i[i])
data2_22=[]
for i in m2m2:
	data2_22.append(dat_i[i])
data2_23=[]
for i in m2m3:
	data2_23.append(dat_i[i])
data2_24=[]
for i in m2m4:
	data2_24.append(dat_i[i])

# get resistances
#data3_11=[]
#for k in range(len(data2_11)):
#	data3_11.append(voltages_11[k]/data2_11[k])
data3_12=[]
for k in range(len(data2_12)):
	data3_12.append(voltages_12[k]/data2_12[k])
data3_13=[]
for k in range(len(data2_13)):
	data3_13.append(voltages_13[k]/data2_13[k])
data3_14=[]
for k in range(len(data2_14)):
	data3_14.append(voltages_14[k]/data2_14[k])
data3_21=[]
for k in range(len(data2_21)):
	data3_21.append(voltages_21[k]/data2_21[k])
data3_22=[]
for k in range(len(data2_22)):
	data3_22.append(voltages_22[k]/data2_22[k])
data3_23=[]
for k in range(len(data2_23)):
	data3_23.append(voltages_23[k]/data2_23[k])
data3_24=[]
for k in range(len(data2_24)):
	data3_24.append(voltages_24[k]/data2_24[k])

# make the data the right length for plotting, then plot
# m1m1
#klist_11=[]
#for k in range(len(data3_11)):
#	ilist11=[]
#	for i in range(len(data3_11[k])):
#		if i%((len(data2_11)/len(temps))+1)==0:
#			ilist11.append(data3_11[k][i])
#	klist_11.append(list(ilist11))
#temps_11=temps
#while len(temps_11)!=len(klist_11[0]):
#	temps_11.remove(temps_11[0])
#for i in range(len(klist_11)):
#	plt.plot(temps_11,klist_11[i])

# m1m2
klist_12=[]
for k in range(len(data3_12)):
	ilist12=[]
	for i in range(len(data3_12[k])):
		ilist12.append(data3_12[k][i])
	klist_12.append(list(ilist12))
temps_12=temps
while len(temps_12)!=len(klist_12[0]):
	temps_12.remove(temps_12[0])
for i in range(len(klist_12)):
	plt.plot(temps_12,klist_12[i])
	plt.show()

# m1m3
klist_13=[]
for k in range(len(data3_13)):
	ilist13=[]
	for i in range(len(data3_13[k])):
		ilist13.append(data3_13[k][i])
	klist_13.append(list(ilist13))
temps_13=temps
while len(temps_13)!=len(klist_13[0]):
	temps_13.remove(temps_13[0])
#for i in range(len(klist_13)):
#	plt.plot(temps_13,klist_13[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 3')

# m1m4
klist_14=[]
for k in range(len(data3_14)):
	ilist14=[]
	for i in range(len(data3_14[k])):
		ilist14.append(data3_14[k][i])
	klist_14.append(list(ilist14))
temps_14=temps
while len(temps_14)!=len(klist_14[0]):
	temps_14.remove(temps_14[0])
#for i in range(len(klist_14)):
#	plt.plot(temps_14,klist_14[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 4')

# m2m1
klist_21=[]
for k in range(len(data3_21)):
	ilist21=[]
	for i in range(len(data3_21[k])):
		ilist21.append(data3_21[k][i])
	klist_21.append(list(ilist21))
temps_21=temps
while len(temps_21)!=len(klist_21[0]):
	temps_21.remove(temps_21[0])
#for i in range(len(klist_21)):
#	plt.plot(temps_21,klist_21[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 5')

# m2m2
klist_22=[]
for k in range(len(data3_22)):
	ilist22=[]
	for i in range(len(data3_22[k])):
		ilist22.append(data3_22[k][i])
	klist_22.append(list(ilist22))
temps_22=temps
while len(temps_22)!=len(klist_22[0]):
	temps_22.remove(temps_22[0])
#for i in range(len(klist_22)):
#	plt.plot(temps_22,klist_22[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 6')

# m2m3
klist_23=[]
for k in range(len(data3_23)):
	ilist23=[]
	for i in range(len(data3_23[k])):
		ilist23.append(data3_23[k][i])
	klist_23.append(list(ilist23))
temps_23=temps
while len(temps_23)!=len(klist_23[0]):
	temps_23.remove(temps_23[0])
#for i in range(len(klist_23)):
#	plt.plot(temps_23,klist_23[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 7')

# m2m4
klist_24=[]
for k in range(len(data3_24)):
	ilist24=[]
	for i in range(len(data3_24[k])):
		ilist24.append(data3_24[k][i])
	klist_24.append(list(ilist24))
temps_24=temps
while len(temps_24)!=len(klist_24[0]):
	temps_24.remove(temps_24[0])
#for i in range(len(klist_24)):
#	plt.plot(temps_24,klist_24[i])
#	plt.xlabel('Temperature (K)')
#	plt.ylabel('Resistance ($\Omega$)')
#	plt.title('R(T) for Wafer 109, SQUID 8')



rnorms=[]

rn12=[]
t_high_index_12=[]
for i in range(len(temps_12)):
	if temps_12[i]>0.580 and temps_12[i]<0.600:
		t_high_index_12.append(i)
highr_12=[]
for i in range(len(klist_12)):
	nums12=[]
	for j in t_high_index_12:
		nums12.append(klist_12[i][j])
	highr_12.append(nums12)

for i in range(len(highr_12)):
	total12=0
	for j in range(len(highr_12[i])):
		total12=total12+highr_12[i][j]
	rnorm12=total12/len(highr_12[i])
	rn12.append(rnorm12)
for r in rn12:
	rnorms.append(r)

rn13=[]
t_high_index_13=[]
for i in range(len(temps_13)):
	if temps_13[i]>0.580 and temps_13[i]<0.600:
		t_high_index_13.append(i)
highr_13=[]
for i in range(len(klist_13)):
	nums13=[]
	for j in t_high_index_13:
		nums13.append(klist_13[i][j])
	highr_13.append(nums13)

for i in range(len(highr_13)):
	total13=0
	for j in range(len(highr_13[i])):
		total13=total13+highr_13[i][j]
	rnorm13=total13/len(highr_13[i])
	rn13.append(rnorm13)
for r in rn13:
	rnorms.append(r)

rn14=[]
t_high_index_14=[]
for i in range(len(temps_14)):
	if temps_14[i]>0.580 and temps_14[i]<0.600:
		t_high_index_14.append(i)
highr_14=[]
for i in range(len(klist_14)):
	nums14=[]
	for j in t_high_index_14:
		nums14.append(klist_14[i][j])
	highr_14.append(nums14)

for i in range(len(highr_14)):
	total14=0
	for j in range(len(highr_14[i])):
		total14=total14+highr_14[i][j]
	rnorm14=total14/len(highr_14[i])
	rn14.append(rnorm14)
for r in rn14:
	rnorms.append(r)

rn21=[]
t_high_index_21=[]
for i in range(len(temps_21)):
	if temps_21[i]>0.550 and temps_21[i]<0.600:
		t_high_index_21.append(i)
highr_21=[]
for i in range(len(klist_21)):
	nums21=[]
	for j in t_high_index_21:
		nums21.append(klist_21[i][j])
	highr_21.append(nums21)

for i in range(len(highr_21)):
	total21=0
	for j in range(len(highr_21[i])):
		total21=total21+highr_21[i][j]
	rnorm21=total21/len(highr_21[i])
	rn21.append(rnorm21)
for r in rn21:
	rnorms.append(r)

rn22=[]
t_high_index_22=[]
for i in range(len(temps_22)):
	if temps_22[i]>0.550 and temps_22[i]<0.630:
		t_high_index_22.append(i)
highr_22=[]
for i in range(len(klist_22)):
	nums22=[]
	for j in t_high_index_22:
		nums22.append(klist_22[i][j])
	highr_22.append(nums22)

for i in range(len(highr_22)):
	total22=0
	for j in range(len(highr_22[i])):
		total22=total22+highr_22[i][j]
	rnorm22=total22/len(highr_22[i])
	rn22.append(rnorm22)
for r in rn22:
	rnorms.append(r)

rn23=[]
t_high_index_23=[]
for i in range(len(temps_22)):
	if temps_23[i]>0.550 and temps_23[i]<0.600:
		t_high_index_23.append(i)
highr_23=[]
for i in range(len(klist_23)):
	nums23=[]
	for j in t_high_index_23:
		nums23.append(klist_23[i][j])
	highr_23.append(nums23)

for i in range(len(highr_23)):
	total23=0
	for j in range(len(highr_23[i])):
		total23=total23+highr_23[i][j]
	rnorm23=total23/len(highr_23[i])
	rn23.append(rnorm23)
for r in rn23:
	rnorms.append(r)

rn24=[]
t_high_index_24=[]
for i in range(len(temps_24)):
	if temps_24[i]>0.580 and temps_24[i]<0.600:
		t_high_index_24.append(i)
highr_24=[]
for i in range(len(klist_24)):
	nums24=[]
	for j in t_high_index_24:
		nums24.append(klist_24[i][j])
	highr_24.append(nums24)

for i in range(len(highr_24)):
	total24=0
	for j in range(len(highr_24[i])):
		total24=total24+highr_24[i][j]
	rnorm24=total24/len(highr_24[i])
	rn24.append(rnorm24)
for r in rn24:
	rnorms.append(r)



rpars=[]

rp12=[]
t_low_index_12=[]
for i in range(len(temps_12)):
	if temps_12[i]>0.440 and temps_12[i]<0.490:
		t_low_index_12.append(i)
lowr_12=[]
for i in range(len(klist_12)):
	lows12=[]
	for j in t_low_index_12:
		if abs(klist_12[i][j])<2.00:
			lows12.append(klist_12[i][j])
	lowr_12.append(lows12)

for i in range(len(lowr_12)):
	lowtotal12=0
	for j in range(len(lowr_12[i])):
		lowtotal12=lowtotal12+lowr_12[i][j]
	rpar12=lowtotal12/len(lowr_12[i])
	rp12.append(rpar12)
for r in rp12:
	rpars.append(r)

rp13=[]
t_low_index_13=[]
for i in range(len(temps_13)):
	if temps_13[i]>0.440 and temps_13[i]<0.490:
		t_low_index_13.append(i)
lowr_13=[]
for i in range(len(klist_13)):
	lows13=[]
	for j in t_low_index_13:
		if abs(klist_13[i][j])<2.00:
			lows13.append(klist_13[i][j])
	lowr_13.append(lows13)

for i in range(len(lowr_13)):
	lowtotal13=0
	for j in range(len(lowr_13[i])):
		lowtotal13=lowtotal13+lowr_13[i][j]
	rpar13=lowtotal13/len(lowr_13[i])
	rp13.append(rpar13)
for r in rp13:
	rpars.append(r)

rp14=[]
t_low_index_14=[]
for i in range(len(temps_14)):
	if temps_14[i]>0.50 and temps_14[i]<0.510:
		t_low_index_14.append(i)
lowr_14=[]
for i in range(len(klist_14)):
	lows14=[]
	for j in t_low_index_14:
		if abs(klist_14[i][j])<2.00:
			lows14.append(klist_14[i][j])
	lowr_14.append(lows14)

for i in range(len(lowr_14)):
	lowtotal14=0
	for j in range(len(lowr_14[i])):
		lowtotal14=lowtotal14+lowr_14[i][j]
	rpar14=lowtotal14/len(lowr_14[i])
	rp14.append(rpar14)
for r in rp14:
	rpars.append(r)

rp21=[]
t_low_index_21=[]
for i in range(len(temps_21)):
	if temps_21[i]>0.400 and temps_21[i]<0.440:
		t_low_index_21.append(i)
lowr_21=[]
for i in range(len(klist_21)):
	lows21=[]
	for j in t_low_index_21:
		if abs(klist_21[i][j])<2.00:
			lows21.append(klist_21[i][j])
	lowr_21.append(lows21)

for i in range(len(lowr_21)):
	lowtotal21=0
	for j in range(len(lowr_21[i])):
		lowtotal21=lowtotal21+lowr_21[i][j]
	rpar21=lowtotal21/len(lowr_21[i])
	rp21.append(rpar21)
for r in rp21:
	rpars.append(r)

rp22=[]
t_low_index_22=[]
for i in range(len(temps_22)):
	if temps_22[i]>0.400 and temps_22[i]<0.440:
		t_low_index_22.append(i)
lowr_22=[]
for i in range(len(klist_22)):
	lows22=[]
	for j in t_low_index_22:
		if abs(klist_22[i][j])<2.00:
			lows22.append(klist_22[i][j])
	lowr_22.append(lows22)

for i in range(len(lowr_22)):
	lowtotal22=0
	for j in range(len(lowr_22[i])):
		lowtotal22=lowtotal22+lowr_22[i][j]
	rpar22=lowtotal22/len(lowr_22[i])
	rp22.append(rpar22)
for r in rp22:
	rpars.append(r)

rp23=[]
t_low_index_23=[]
for i in range(len(temps_23)):
	if temps_23[i]>0.400 and temps_23[i]<0.440:
		t_low_index_23.append(i)
lowr_23=[]
for i in range(len(klist_23)):
	lows23=[]
	for j in t_low_index_23:
		if abs(klist_23[i][j])<2.00:
			lows23.append(klist_23[i][j])
	lowr_23.append(lows23)

for i in range(len(lowr_23)):
	lowtotal23=0
	for j in range(len(lowr_23[i])-1):
		lowtotal23=lowtotal23+lowr_23[i][j]
	rpar23=lowtotal23/len(lowr_23[i])
	rp23.append(rpar23)
for r in rp23:
	rpars.append(r)

rp24=[]
t_low_index_24=[]
for i in range(len(temps_24)):
	if temps_24[i]>0.350 and temps_24[i]<0.440:
		t_low_index_24.append(i)
lowr_24=[]
for i in range(len(klist_24)):
	lows24=[]
	for j in t_low_index_24:
		if abs(klist_24[i][j])<2.00:
			lows24.append(klist_24[i][j])
	lowr_24.append(lows24)

for i in range(len(lowr_24)):
	lowtotal24=0
	for j in range(len(lowr_24[i])):
		lowtotal24=lowtotal24+lowr_24[i][j]
	rpar24=lowtotal24/len(lowr_24[i])
	rp24.append(rpar24)
for r in rp24:
	rpars.append(r)


all_tc=[]

tc12=[]
for j in range(len(klist_12)):
	prime=[]
	for i in range(len(temps_12)):
		if temps_12[i]>0.515 and temps_12[i]<0.600:
			if (klist_12[j][i]<0.8*rn12[j]):
				if (klist_12[j][i]>(rp12[j]+0.2*rn12[j])):
					prime.append(temps_12[i])
	tctotal=0
	for k in range(len(prime)):
		tctotal=tctotal+prime[k]
	tc12.append(tctotal/len(prime))
for l in tc12:
	all_tc.append(l)
bad12=[42,50,51,53,54,56,58,59]

tc13=[]
for j in range(len(klist_13)):
	prime=[]
	for i in range(len(temps_13)):
		if temps_13[i]>0.480 and temps_13[i]<0.600:
			if (klist_13[j][i]<0.9*rn13[j]):
				if (klist_13[j][i]>(rp13[j]+0.1*rn13[j])):
					prime.append(temps_13[i])
	tctotal=0
	for k in range(len(prime)):
		tctotal=tctotal+prime[k]
	tc13.append(tctotal/len(prime))
for l in tc13:
	all_tc.append(l)
bad13=[12,21]


tc14=[]
gone_14=[]
for j in range(len(klist_14)):
	prime=[]
	for i in range(len(temps_14)):
		if temps_14[i]>0.505 and temps_14[i]<0.600:
			if (klist_14[j][i]<0.9*rn14[j]):
				if (klist_14[j][i]>(rp14[j]+0.1*rn14[j])):
					prime.append(temps_14[i])
	if len(prime)!=0:
		tctotal=0
		for k in range(len(prime)):
			tctotal=tctotal+prime[k]
		tc14.append(tctotal/len(prime))
	else:
		gone_14.append(j)
print 'The length of gone_14 is ' + str(len(gone_14))
#do this after plotting gone_14 channels
for l in range(len(gone_14)):
	m1m4_nope.append('Gone: '+str(m1m4[gone_14[l]]))
	m1m4.remove(m1m4[gone_14[-l]])
	klist_14.remove(klist_14[gone_14[-l]])
	rn14.remove(rn14[gone_14[-l]])
	rp14.remove(rp14[gone_14[-l]])
	

for l in tc14:
	all_tc.append(l)
bad14=[3,17,20,23,24,31,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53]
for n in bad14:
	all_tc.remove(tc14[n])

gone_21=[]
tc21=[]
for j in range(len(klist_21)):
	prime=[]
	for i in range(len(temps_21)):
		if temps_21[i]>0.450 and temps_21[i]<0.600:
			if (klist_21[j][i]<0.8*rn21[j]):
				if (klist_21[j][i]>(rp21[j]+0.1*rn21[j])):
					prime.append(temps_21[i])
	if len(prime)!=0:
		tctotal=0
		for k in range(len(prime)):
			tctotal=tctotal+prime[k]
		tc21.append(tctotal/len(prime))
	else:
		gone_21.append(j)
for l in tc21:
	all_tc.append(l)
bad21=[2,4,6,11,29,30,45,46]

gone_22=[]
tc22=[]
for j in range(len(klist_22)):
	prime=[]
	for i in range(len(temps_22)):
		if temps_22[i]>0.460 and temps_22[i]<0.530:
			if (klist_22[j][i]<0.9*rn22[j]):
				if (klist_22[j][i]>(rp22[j]+0.1*rn22[j])):
					prime.append(temps_22[i])
	if len(prime)!=0:
		tctotal=0
		for k in range(len(prime)):
			tctotal=tctotal+prime[k]
		tc22.append(tctotal/len(prime))
	else:
		gone_22.append(j)
for l in tc22:
	all_tc.append(l)
bad22=[0,5,13,20,31,37,38,39,40,41,42,43,44,50,52]

gone_23=[]
tc23=[]
for j in range(len(klist_23)):
	prime=[]
	for i in range(len(temps_23)):
		if temps_23[i]>0.400 and temps_21[i]<0.600:
			if (klist_23[j][i]<0.9*rn23[j]):
				if (klist_23[j][i]>(rp23[j]+0.1*rn23[j])):
					prime.append(temps_23[i])
	if len(prime)!=0:
		tctotal=0
		for k in range(len(prime)):
			tctotal=tctotal+prime[k]
		tc23.append(tctotal/len(prime))
	else:
		gone_23.append(j)
for l in tc23:
	all_tc.append(l)
bad23=[9,34]

gone_24=[]
tc24=[]
for j in range(len(klist_24)):
	prime=[]
	for i in range(len(temps_24)):
		if temps_24[i]>0.510 and temps_24[i]<0.600:
			if (klist_24[j][i]<0.8*rn24[j]):
				if (klist_24[j][i]>(rp24[j]+0.2*rn24[j])):
					prime.append(temps_24[i])
	if len(prime)!=0:
		tctotal=0
		for k in range(len(prime)):
			tctotal=tctotal+prime[k]
		tc24.append(tctotal/len(prime))
	else:
		gone_24.append(j)	
for l in tc24:
	all_tc.append(l)
bad24=[3,4,19,32,35,41,42,43,44,45,46,47,49,50,51,52,53,54,56,57,58,59,60]

# plotters (run in ipython --pylab)
def plotter12():
	for ind in range(len(klist_12)):
		plt.plot(temps_12,klist_12[ind],color='b')
		plt.axhline(y=rn12[ind], color='g')
		plt.axhline(y=rp12[ind], color='g')
		plt.axvline(x=tc12[ind], color='r')
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m1m2[ind]) +'\n Press enter to continue...')
def plotter13():
	for ind in range(len(klist_13)):
		plt.plot(temps_13,klist_13[ind],color='b')
		plt.axhline(y=rn13[ind], color='g')
		plt.axhline(y=rp13[ind], color='g')
		plt.axvline(x=tc13[ind], color='r')
		plt.title('Mezz 1 Mod 3 Index ' + str(ind))
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m1m3[ind]) +'\n Press enter to continue...')
def plotter14():
	for ind in range(len(klist_14)):
		plt.plot(temps_14,klist_14[ind],color='b')
		plt.axhline(y=rn14[ind], color='g')
		plt.axhline(y=rp14[ind], color='g')
		plt.axvline(x=tc14[ind], color='r')
		plt.title('Mezz 1 Mod 4 Index ' + str(ind))
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m1m4[ind]) +'\n Press enter to continue...')
def plotter21():
	for ind in range(len(klist_21)):
		plt.plot(temps_21,klist_21[ind],color='b')
		plt.axhline(y=rn21[ind], color='g')
		plt.axhline(y=rp21[ind], color='g')
		plt.axvline(x=tc21[ind], color='r')
		plt.title('Mezz 2 Mod 1 Index ' + str(ind))
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m2m1[ind]) +'\n Press enter to continue...')
def plotter22():
	for ind in range(len(klist_22)):
		plt.plot(temps_22,klist_22[ind],color='b')
		plt.axhline(y=rn22[ind], color='g')
		plt.axhline(y=rp22[ind], color='g')
		plt.axvline(x=tc22[ind], color='r')
		plt.title('Mezz 2 Mod 2 Index ' + str(ind))	
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m2m2[ind]) +'\n Press enter to continue...')
def plotter23():
	for ind in range(len(klist_23)):
		plt.plot(temps_23,klist_23[ind],color='b')
		plt.axhline(y=rn23[ind], color='g')
		plt.axhline(y=rp23[ind], color='g')
		plt.axvline(x=tc23[ind], color='r')
		plt.title('Mezz 2 Mod 3 Index '+str(ind))
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m2m3[ind]) +'\n Press enter to continue...')
def plotter24():
	for ind in range(len(klist_24)):
		plt.plot(temps_24,klist_24[ind],color='b')
		plt.axhline(y=rn24[ind], color='g')
		plt.axhline(y=rp24[ind], color='g')
		plt.axvline(x=tc24[ind], color='r')
		plt.title('Mezz 2 Mod 4 Index ' + str(ind))	
		plt.show()
		raw_input ('You are looking at bolometer ' + str(m2m4[ind]) +'\n Press enter to continue...')



# remove "bad" and "gone" channels (based on plotting)
def rmbolos():
	for qq in bad12:
		m1m2_nope.append('Bad curve: ' + str(m1m2[qq]))
		m1m2.remove(m1m2[qq])
		klist_12.remove(klist_12[qq])
		rp12.remove(rp12[qq])
		rn12.remove(rn12[qq])
	for qq in bad13:
		m1m3_nope.append('Bad curve: ' + str(m1m3[qq]))
		m1m3.remove(m1m3[qq])
		klist_13.remove(klist_13[qq])
		rp13.remove(rp13[qq])
		rn13.remove(rn13[qq])
	for qq in bad14:
		m1m4_nope.append('Bad curve: ' + str(m1m4[qq]))
		m1m4.remove(m1m4[qq])
		klist_14.remove(klist_14[qq])
		rp14.remove(rp14[qq])
		rn14.remove(rn14[qq])
	for qq in bad21:
		m2m1_nope.append('Bad curve: ' + str(m2m1[qq]))
		m2m1.remove(m2m1[qq])
		klist_21.remove(klist_21[qq])
		rp21.remove(rp21[qq])
		rn21.remove(rn21[qq])
	for qq in bad22:
		m2m2_nope.append('Bad curve: ' + str(m2m2[qq]))
		m2m2.remove(m2m2[qq])
		klist_22.remove(klist_22[qq])
		rp22.remove(rp22[qq])
		rn22.remove(rn22[qq])
	for qq in bad23:
		m2m3_nope.append('Bad curve: ' + str(m2m3[qq]))
		m2m3.remove(m2m3[qq])
		klist_23.remove(klist_23[qq])
		rp23.remove(rp23[qq])
		rn23.remove(rn23[qq])
	for qq in bad24:
		m2m4_nope.append('Bad curve: ' + str(m2m4[qq]))
		m2m4.remove(m2m4[qq])
		klist_24.remove(klist_24[qq])
		rp24.remove(rp24[qq])
		rn24.remove(rn24[qq])
	
# make a dictionary
def store_results():
	results={}
#	for i in range(len(m1m2)):
#		results[str(m1m2[i])]={'rpar':rp12[i],'rtotal':rn12[i],'tc':tc12[i],'band':str(m1m2[i]).split('.')[2]}
#	for i in range(len(m1m3)):
#		results[str(m1m3[i])]={'rpar':rp13[i],'rtotal':rn13[i],'tc':tc13[i],'band':str(m1m3[i]).split('.')[2]}
#	for i in range(len(m1m4)):
#		results[str(m1m4[i])]={'rpar':rp14[i],'rtotal':rn14[i],'tc':tc14[i],'band':str(m1m4[i]).split('.')[2]}
	for i in range(len(m2m1)):
		results[str(m2m1[i])]={'rpar':rp21[i],'rtotal':rn21[i],'tc':tc21[i],'band':str(m2m1[i]).split('.')[2]}
	for i in range(len(m2m2)):
		results[str(m2m2[i])]={'rpar':rp22[i],'rtotal':rn22[i],'tc':tc22[i],'band':str(m2m2[i]).split('.')[2]}
	for i in range(len(m2m3)):
		results[str(m2m3[i])]={'rpar':rp23[i],'rtotal':rn23[i],'tc':tc23[i],'band':str(m2m3[i]).split('.')[2]}
#	for i in range(len(m2m4)):
#		results[str(m2m4[i])]={'rpar':rp24[i],'rtotal':rn24[i],'tc':tc24[i],'band':str(m2m4[i]).split('.')[2]}

	f=open('/home/spt3g/ledgerman_output/20161209/rt_results_20161209.pkl','w')
	pickle.dump(results,f)
	f.close()
	
	return results

my_res=store_results()

tc90=[]
tc150=[]
tc220=[]
for i in my_res:
	if my_res[i]['band']=='90':
		tc90.append(my_res[i]['tc'])
	if my_res[i]['band']=='150':
		tc150.append(my_res[i]['tc'])
	if my_res[i]['band']=='220':
		tc220.append(my_res[i]['tc'])
plt.hist(tc90,color='y',alpha=0.3,label='90 GHz')
plt.hist(tc150,color='c',alpha=0.3,label='150 GHz')
plt.hist(tc220,color='r',alpha=0.3,label='220 GHz')
plt.title('$T_C$ for Wafer 132 (by band)')
plt.xlabel('$T_C$ (K)')
plt.ylabel('Number of bolometers')
plt.legend()

