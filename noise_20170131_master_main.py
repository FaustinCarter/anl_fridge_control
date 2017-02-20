import pydfmux
import numpy as np
import cPickle as pkl
import time
import os
from pydfmux.core.utils.conv_functs import build_hwm_query
import glob
import sys
from he10_fridge_control.Lauren.std_print import Logger
#from git_repos.hardware_maps.do_noise_loop import do_noise_loop

sleep_time = False # in min
if sleep_time:
    total_sleep_sec = sleep_time*60
    cumul_time = 0
    while cumul_time < total_sleep_sec:
        print 'waited '+str(cumul_time/60.)+' min of '+str(total_sleep_sec/60.)+' min so far'
        time.sleep(60)
        cumul_time+=60

output_dir = '/home/spt3g/output/20170203/noise_sweep/'
################# Update the file below
output_file = output_dir+'noise_amp_sweep_600/noise_600mK.txt'
stdout_file = output_file.rstrip('.txt')+'_stdout.txt'
sys.stdout = Logger(stdout_file)

#all_chans = True; use_chans=False
all_chans = False; use_chans = True; chans = [1,2,31,45,57,58]
#all_chans = False; use_chans = True; chans = [35]
#all_chans = False; use_chans = True; chans = np.arange(0,30)

#amps = np.linspace(0.001,0.02,20)[::2] # these are the nominal amps
# amps = np.linspace(0.001,0.02,20)[:-5:4]
amps = np.linspace(0.001,0.02,20)


freq_quant = 20e6/262144. # 76.2939453125 Hz
#freq_shifts = [0]#np.linspace(-1,1,3)*freq_quant
# freq_shifts = np.linspace(-60,60,13)*freq_quant
freq_shifts = np.array([0])*freq_quant

for _out in [output_file]:
    if os.path.isfile(_out):
        print 'your file already exists, try again'
        exit()
    log_info = open(output_file,'w')
log_info.write('amp \t freq_shift \t overbias_file \t DAN_on_dump \t DAN_on_Z_squid \t DAN_off_dump \t DAN_off_Z_squid \n')

############################## CONFIGURATION ###################################
hwm_location       = '/home/spt3g/hardware_maps/hwm_anl_20170201_Nb_and_Al/hwm_anl_complete.yml'
cut_on_transimpedance = False  # Only use SQUIDs that have good transimpedance
# NOTE: This requires that tune_squids=True
transimpedance_cut = 300    # Ohms
target_lowgain     = 10    # The lowest-noise gain setting you want to reach
use_test_IRIG      = True   # For setups without external IRIG
cold_overbias      = False  # For setups with cold overbias-able bolometers
serialize          = False  # Debugging option to run most algorithms in serial
# not asynchronously (/parallel)

# Load Hardware Map and query it for the objects we will use
s      = pydfmux.load_session(file(hwm_location))
hwm    = s['hardware_map']
ds     = hwm.query(pydfmux.Dfmux) # dfmux boards
sqcbs  = hwm.query(pydfmux.SQUIDController) # squid controllers
squids = hwm.query(pydfmux.SQUID) # actual squids
rmods  = hwm.query(pydfmux.ReadoutModule) # readout modules?


# --- below is for the bolos on mezz1
sqcbs = hwm.query(pydfmux.SQUIDController).filter(pydfmux.SQUIDController.serial=='06-01')
squids_ = hwm.query(pydfmux.SQUID).join(pydfmux.SQUIDModule,pydfmux.SQUIDController,pydfmux.MGMEZZ04).filter(pydfmux.MGMEZZ04.serial.in_(['160']),pydfmux.SQUIDModule.module.in_([1]))
rmods_ = hwm.query(pydfmux.ReadoutModule).join(pydfmux.MGMEZZ04,pydfmux.SQUIDController,pydfmux.SQUIDModule).filter(pydfmux.MGMEZZ04.serial.in_(['160']),pydfmux.ReadoutModule.module.in_([1]))

#mezz 2 - bolos
sqcbs = hwm.query(pydfmux.SQUIDController).filter(pydfmux.SQUIDController.serial=='06-02')
squids = squids_.union(hwm.query(pydfmux.SQUID).join(pydfmux.SQUIDModule,pydfmux.SQUIDController,pydfmux.MGMEZZ04).filter(pydfmux.MGMEZZ04.serial.in_(['161']),pydfmux.SQUIDModule.module.in_([4])))
rmods = rmods_.union(hwm.query(pydfmux.ReadoutModule).join(pydfmux.MGMEZZ04,pydfmux.SQUIDController,pydfmux.SQUIDModule).filter(pydfmux.MGMEZZ04.serial.in_(['161']),pydfmux.ReadoutModule.module.in_([4])))


if all_chans:
    print 'using all channels'

#################


def main():
    # we need this dict because we constantly overwrite the frequencies in the hardware maps
    orig_freq_dict = dict({})

    if all_chans:
        bolos_overbias = get_bolos(all_chans=True)
    else:
        bolos_overbias = get_bolos(all_chans=False,chans = chans, use_chans=True)

    # save the original freqs to a dict
    for _bnum,_bolo in enumerate(bolos_overbias):
        orig_freq_dict[_bolo] =  _bolo.channel_map.lc_channel.frequency
    for _fnum,_freq_shift in enumerate(freq_shifts):
        print str(_fnum+1) +' of '+str(len(freq_shifts))+'  freq shifts'
        print 'starting freq shfit '+ str(_freq_shift)

        for _anum,_amp in enumerate(amps):
            print str(_anum+1) +' of '+str(len(amps))+'  amps'
            print 'starting amp'+ str(_amp)
            print 'still on '+str(_fnum) +' of '+str(len(freq_shifts))+'  freq shifts'

            print 'freq_shift = ',_freq_shift
            print 'amp = ',_amp
            log_info.write(str(_amp)+' \t'+str(_freq_shift)+' \t')

            do_noise_loop(_amp,_freq_shift,bolos_overbias,orig_freq_dict,overbias=True)

def do_noise_loop(_amp,_freq_shift,bolos_overbias,orig_freq_dict,overbias=True):
    if overbias:
        ds.clear_all()
        ds.clear_dan()
        print 'combs are now zeroed'

    for _bnum,_bolo in enumerate(bolos_overbias):
        _bolo.channel_map.lc_channel.frequency = orig_freq_dict[_bolo]+_freq_shift
        _bolo.hwm.commit()
#    print orig_freq_dict
    print ['m'+str( _sq.readout_module.module)+'s'+str(_sq.readout_module.mezzanine.mezzanine)+'='+str( _sq.calc_Z_analytic()) for _sq in squids]

    if overbias:
    # Overbias and enable DAN for nulling
        print 'overbiasing %i'%(len(bolos_overbias.all()))
        OB_results = bolos_overbias.overbias_and_null(cold_overbias=cold_overbias,
                                                      serialize=serialize,
                                                      shorted_threshold=.01,
                                                      max_resistance=15,
                                                      bias_power=False,
                                                      carrier_amplitude=_amp,
                                                      scale_by_frequency=False,
                                                      use_dan_gain=0.005)
        for _key in OB_results:
            if _key is not 'output_directory':
                print OB_results[_key]['reduced_target']+' --> '+OB_results[_key]['outcome']
        print 'done biasing'
        print max(glob.iglob(output_dir+'/*'), key=os.path.getctime).split('/')[-1]
        log_info.write(max(glob.iglob(output_dir+'/*'), key=os.path.getctime))
        log_info.write('\t')

    else:
        log_info.write('no_biasing_perfromed')
        log_info.write('\t')
        chans = build_hwm_query(bolos_overbias.readout_channel)
        chans.enable_dan(start_from_static_nulling=False)

    print 'getting DAN-noise'
    bolos_tune = bolos_overbias.filter(pydfmux.Bolometer.tune==True)
    bolos_tune.dump_info(take_noise=True, nsamps=1000)
    print max(glob.iglob(output_dir+'/*'), key=os.path.getctime).split('/')[-1]
    log_info.write(max(glob.iglob(output_dir+'/*'), key=os.path.getctime))# dan on info
    log_info.write('\t')
    for _sq in squids:
        log_info.write('m'+str(_sq.readout_module.mezzanine.mezzanine)+'s'+str( _sq.readout_module.module)+'='+str( _sq.calc_Z_analytic())+',')
    log_info.write('\t')
    print ['m'+str(_sq.readout_module.mezzanine.mezzanine)+'s'+str( _sq.readout_module.module)+'='+str( _sq.calc_Z_analytic()) for _sq in squids]

    print 'turning DAN off'
    chans = build_hwm_query(bolos_overbias.readout_channel)
    chans.disable_dan(update_static_nulling=True)

    print 'getting DAN-off Noise'
    bolos_tune.dump_info(take_noise=True, nsamps=1000)
    print max(glob.iglob(output_dir+'/*'), key=os.path.getctime).split('/')[-1]
    log_info.write(max(glob.iglob(output_dir+'/*'), key=os.path.getctime))# dan off noise
    log_info.write('\t')

    print ['m'+str(_sq.readout_module.mezzanine.mezzanine)+'s'+str( _sq.readout_module.module)+'='+str( _sq.calc_Z_analytic()) for _sq in squids]
    for _sq in squids:
        log_info.write('m'+str(_sq.readout_module.mezzanine.mezzanine)+'s'+str( _sq.readout_module.module)+'='+str( _sq.calc_Z_analytic())+',')
    log_info.write('\n')

    print '-----------------------------------'
    print '-----------------------------------'
    print '-----------------------------------'


def get_bolos(all_chans=False,use_chans=False,chans=None):
    if all_chans:
        bolos_overbias = hwm.query(pydfmux.Bolometer).join(pydfmux.ChannelMapping,pydfmux.SQUID,
                                                           pydfmux.SQUIDModule,
                                                           pydfmux.SQUIDController,
                                                           pydfmux.MGMEZZ04,
                                                           pydfmux.ReadoutChannel).filter(pydfmux.MGMEZZ04.serial.in_(['160']),
                    					                   pydfmux.Bolometer.overbias==True,
                    					                   pydfmux.SQUIDModule.module.in_([1]))

        bolos_overbias = bolos_overbias.union(hwm.query(pydfmux.Bolometer).join(pydfmux.ChannelMapping,pydfmux.SQUID,
                                                                               pydfmux.SQUIDModule,
                                                                               pydfmux.SQUIDController,
                                                                               pydfmux.MGMEZZ04,
                                                                               pydfmux.ReadoutChannel).filter(pydfmux.MGMEZZ04.serial.in_(['161']),
                                    									       pydfmux.Bolometer.overbias==True,
                                    									       pydfmux.SQUIDModule.module.in_([4]),))
    elif use_chans:
        bolos_overbias = hwm.query(pydfmux.Bolometer).join(pydfmux.ChannelMapping,pydfmux.SQUID,
                                                           pydfmux.SQUIDModule,
                                                           pydfmux.SQUIDController,
                                                           pydfmux.MGMEZZ04,
                                                           pydfmux.ReadoutChannel).filter(pydfmux.MGMEZZ04.serial.in_(['160']),
                				                           pydfmux.Bolometer.overbias==True,
                				                           pydfmux.SQUIDModule.module.in_([1]),
                				                           pydfmux.ReadoutChannel.channel.in_(chans))

        bolos_overbias = bolos_overbias.union(hwm.query(pydfmux.Bolometer).join(pydfmux.ChannelMapping,pydfmux.SQUID,
                                                                                pydfmux.SQUIDModule,
                                                                                pydfmux.SQUIDController,
                                                                                pydfmux.MGMEZZ04,
                                                                                pydfmux.ReadoutChannel).filter(pydfmux.MGMEZZ04.serial.in_(['161']),
                                        										pydfmux.Bolometer.overbias==True,
                                        										pydfmux.SQUIDModule.module.in_([4]),
                                        										pydfmux.ReadoutChannel.channel.in_(chans)))



    return bolos_overbias

if __name__ == '__main__':
    main()
