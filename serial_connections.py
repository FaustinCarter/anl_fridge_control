import anl_fridge_control.powersupply as PS
import anl_fridge_control.lakeshore as LS

# power supplies
He4p=PS.PowerSupply('He4p.txt')
He4s=PS.PowerSupply('He4s.txt')
He3ICp=PS.PowerSupply('He3ICp.txt')
He3ICs=PS.PowerSupply('He3ICs.txt')
He3UCp=PS.PowerSupply('He3UCp.txt')
He3UCs=PS.PowerSupply('He3UCs.txt')

# Lakeshore340 box
channel_of_interest = 'A'
PID_channel = 'A'
ChaseLS=LS.TempControl('/dev/ttyr18', ['A','B','C1','C2'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)
