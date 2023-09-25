from pyvisa import ResourceManager
import time


# install NI-VISA
#create a resource manager
rm = ResourceManager
#print(rm.list_resources())
print(f'Resources detected\n{rm.list_resources()}\n')
# ('USB0::0x1AB1::0x0E11::DP8C1234567890::INSTR', 'ASRL1::INSTR', , TCPIP0::1.2.3.4::56789::SOCKET')
# https://pyvisa.readthedocs.io/en/1.8/names.html

with rm.open_resource("TCPIP::192.168.1.10::INSTR") as power_supply_unit:

    # read instrument *IDN?
    print(power_supply_unit.query('*IDN?'))
    time.sleep(0.2)
    # Reset , outputs revert to OFF
    power_supply_unit.write('*RST')
    time.sleep(0.2)

    # select channel NR 1|2|3|4
    channel = 1
    power_supply_unit.write(f'INST OUT{channel}')

    # select voltage,current
    voltage = 24 # [V]
    current = 0.2 # [A]
    power_supply_unit.write(f'APPLY {voltage},{current}')
    # set OVP + 10%
    power_supply_unit.write(f'VOLT:PROT {voltage+voltage*0.1}')

    # set fuse on/off
    fuse = True
    if fuse:
        power_supply_unit.write('FUSE ON')
    else:
        power_supply_unit.write('FUSE OFF')

    fuse_delay = 50 # [msec.]

    # Defines a fuse delay
    power_supply_unit.write(f'FUSE:DEL {fuse_delay}')

    # Turning on/off the output
    output_state = True
    if output_state:
        power_supply_unit.write('OUTP ON')
    else:
        power_supply_unit.write('OUTP OFF')

    time.sleep(0.2)

