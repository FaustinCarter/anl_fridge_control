import tables
import numpy as np
import scipy
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF

cfp = convert_TF(15, 'carrier',unit='RAW')

def read_temps(datafile, sensor='UC Head', starttime=1489167738.36, endtime=1489178950.07):
	dataread = tables.open_file(datafile, 'r')
	datatable = dataread.get_node('/data/' + sensor.replace(' ', '_'))

	for t in range(int(starttime), int(endtime+1)):
		temp_vals = [row[sensor] for row in datatable.iterrows() if row['time'] > starttime and row['time'] < endtime]
		time_vals = [row['time'] for row in datatable.iterrows() if row['time'] > starttime and row['time'] < endtime]

	dataread.close()

	return temp_vals, time_vals


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
    return data_i, data_q, time_sec


def make_IvT_function(data_i, time_sec, time_vals, temp_vals):
    for tt in time_sec:
        downsample_inds = []
        if time_sec[np.where(time_sec==tt)][0] % 217 == 0:
            downsample_inds.append(time_sec.index(tt))
            sample_ixs = []
            sample_times = []
            sample_temps = []
            for tm in time_vals:
                if (tt-5)<=tm<=(tt+5):
                    sample_ixs.append(time_vals.index(time))
            for ix in sample_ixs:
                sample_times.append(time_vals[ix])
                sample_temps.append(temp_vals[ix])
            tt_fit = scipy.interpolate.interp1d(sample_times, sample_temps)
            print tt_fit
