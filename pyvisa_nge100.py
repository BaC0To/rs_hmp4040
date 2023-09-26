
import time
import pyvisa


# install NI-VISA
#create a resource manager
VENDOR_ID = '0x0AAD' # Rohde & Schwarz VID_0x0AAD
rm = pyvisa.ResourceManager()
instr_list = rm.list_resources()

#print(f'The resource list contains : {instr_list}')

_index = None
counter = 0

for item in instr_list:
    if item.find(VENDOR_ID) != -1:
        _index = counter
    counter += 1

for i, instrument in enumerate(instr_list):
    _index = i if instrument.find(VENDOR_ID) != -1 else _index


resource_string_1 = instr_list[_index]


with rm.open_resource(resource_string_1) as power_supply_unit:


    # read instrument *IDN?
    idn = power_supply_unit.query('*IDN?')
    manufacturer, device_type, part_sn_number, fw_ver = idn.split(',')
    print(
        "--- PSU details ---\n"
        f"Manufacturer: {manufacturer}\n"
        f"Device_Type: {device_type}\n"
        f"Part_ Number/Serial: {part_sn_number}\n"
        f"FW_Ver: {fw_ver.strip()}"
    )

    # Reset , outputs revert to OFF
    power_supply_unit.write('*RST')
    
    # select channel NR 1|2
    channel = 1
    power_supply_unit.write(f'INST OUT{channel}')

    # select voltage,current
    voltage = 24 # [V]
    current = 0.2 # [A]
    power_supply_unit.write(f'APPLY "{voltage},{current}"')

    # set OVP + 10%
    power_supply_unit.write(f'VOLT:PROT:MODE PROT')
    ovp_value = voltage + voltage*0.1
    power_supply_unit.write(f'VOLT:PROT:LEV {ovp_value}')
   
    fuse_delay = 0.05 # [sec.]

    # Defines a fuse delay
    power_supply_unit.write(f'FUSE:DEL {fuse_delay}')
    # set fuse on/off
    fuse = True
    if fuse:
        power_supply_unit.write('FUSE ON')
    else:
        power_supply_unit.write('FUSE OFF')

    output_state = True

    if output_state:
        power_supply_unit.write('OUTP ON')
    else:
        power_supply_unit.write('OUTP OFF')

    time.sleep(3)

    output_state = False

    if output_state:
        power_supply_unit.write('OUTP ON')
    else:
        power_supply_unit.write('OUTP OFF')

    
    general_output_state = False

    time.sleep(0.2)
    state = "ON" if general_output_state else "OFF"
    power_supply_unit.write(f'OUTPut:GENeral {state}')


    # Return to local
    power_supply_unit.write(f'SYSTem:LOCal')
