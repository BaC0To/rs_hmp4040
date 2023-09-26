import pyvisa
import time


rm = pyvisa.ResourceManager()
print(rm.list_resources())

with rm.open_resource('USB0::0x0AAD::0x0197::5601.3800k02-101611::INSTR') as power_supply_unit:
    # read instrument *IDN?
    print(power_supply_unit.query('*IDN?'))
    time.sleep(0.2)
    # Reset , outputs revert to OFF
    power_supply_unit.write('*RST')
    time.sleep(0.2)