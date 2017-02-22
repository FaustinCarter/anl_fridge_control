import anl_fridge_control.powersupply as PS
import anl_fridge_control.lakeshore as LS

# power supplies
He4p=PS.PowerSupply(1,1)
He4s=PS.PowerSupply(1,2)
He3ICp=PS.PowerSupply(2,1)
He3ICs=PS.PowerSupply(2,2)
He3UCp=PS.PowerSupply(3,1)
He3UCs=PS.PowerSupply(3,2)

# Lakeshore340 box
channel_of_interest = 'A'
PID_channel = 'A'
ChaseLS=LS.TempControl('/dev/ttyr18', ['A','B','C1','C2'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)
