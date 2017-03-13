import pickle
import tables
import numpy as np
import scipy
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF

cfp = convert_TF(15, 'carrier',unit='RAW')

def read_temps(tempfile, sensor='UC Head', starttime=1489167738.36, endtime=1489178950.07):
	dataread = tables.open_file(tempfile, 'r')
	datatable = dataread.get_node('/data/' + sensor.replace(' ', '_'))

	for t in range(int(starttime), int(endtime+1)):
		temp_vals = [row[sensor] for row in datatable.iterrows() if row['time'] > starttime and row['time'] < endtime]
		time_vals = [row['time'] for row in datatable.iterrows() if row['time'] > starttime and row['time'] < endtime]

	dataread.close()

	return temp_vals, time_vals


def read_netcdf_fast(ledgerman_filename,cal_factor_pa=cfp):

    data=Dataset(ledgerman_filename,'r',format='NETCDF4')
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
    return data_i, data_q, time_sec


def downsample_data(data_i):
    # make a list of indices, every third index in the ledgerman file
    linds = []
    ind = 0
    while ind < len(time_sec):
        linds.append(ind)
        ind += 3

    # downsample the current data from the ledgerman file
    data_downsample=dict()
    for key in data_i.keys():
        data_downsample[key] = []
        for lind in linds:
            data_downsample[key].append(data_i[key][lind])

    return data_downsample


def pickle_data(data_downsample, temp_vals, filename):
    f=open(filename, 'w')
    pickle.dump({"temp_vals":temp_vals, "data":data_downsample}, f)
    f.close()
