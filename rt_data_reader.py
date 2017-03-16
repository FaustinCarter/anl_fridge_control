import pickle
import tables
import numpy as np
import math
import scipy
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF


#def make_ob_dict(overbias_dir):
    

cfp = convert_TF(15, 'carrier',unit='RAW')

flex_to_mezzmods = {'0137':{'14':'13', '11':'14', '21':'21', '17':'23'}, '0135':{'27':'11'}}


def read_temps(tempfile, sensor='UC Head', starttime=1489595720.07, endtime=1489595780.16):
	dataread = tables.open_file(tempfile, 'r')
	datatable = dataread.get_node('/data/' + sensor.replace(' ', '_'))

	temp_vals = [row[sensor] for row in datatable.iterrows() if row['time'] > starttime-1 and row['time'] < endtime+1]
	time_vals = [row['time'] for row in datatable.iterrows() if row['time'] > starttime-1 and row['time'] < endtime+1]

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


def model_temps(temp_vals, time_vals):
    new_time_vals = np.array(time_vals)-time_vals[0]
    tempfit = scipy.interpolate.interp1d(new_time_vals, temp_vals)
    return tempfit

def downsample_data(time_sec, data_i, data_q, tempfit):
    interp_temps = tempfit(time_sec[0:-3])
        
    ixs = []
    ix0 = 0
    while ix0 < len(time_sec):
        ixs.append(ix0)
        ix0 += 2
    ixs.remove(ixs[-1])
    ds_data = dict()
    for key in data_i.keys():
        ds_data[key] = []
        for ix in ixs:
            ds_data[key].append(math.sqrt(data_i[key][ix]**2+data_q[key][ix]**2))
    ds_temps = []
    for ix in ixs:
        ds_temps.append(interp_temps[ix])

    return ds_temps, ds_data

def pickle_data(ds_temps, ds_data, filename):
    f=open(filename, 'w')
    pickle.dump({"temps":ds_temps, "data":ds_data}, f)
    f.close()

def convert_i2r(ds_data, board, overbias_dir):
    data_r = dict()
    for fc in flex_to_mezzmods[board]:
        f=open(overbias_dir+'IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl', 'r')
        ob = pickle.load(f)
        f.close()

        for ky in ds_data:
            for key in ob['subtargets'].keys():
                if ob['subtargets'][key]['bolometer'].replace('/','_')==str(ky):
                    ds_div=[]
                    for point in ds_data[ky]:
                        if key in ob['overbiased'].keys():
                            ds_div.append(ob['overbiased'][key]['V']/point)
                    data_r[ky] = ds_div

    return data_r
