

import time
import pyvisa

VENDOR_ID = '0x0AAD' # Rohde & Schwarz VID_0x0AAD
rm = pyvisa.ResourceManager()
instr_list = rm.list_resources()
psu_units_available = []

for instrument in (instr_list):
    if instrument.find(VENDOR_ID) != -1:
        psu_units_available.append(instrument)

if len(psu_units_available) != 0 :
    for instrument in psu_units_available:
        try:
            with rm.open_resource(instrument) as power_supply_unit:

                print(power_supply_unit.query('*IDN?'))
                time.sleep(0.2)
                power_supply_unit.write('*RST')
                time.sleep(0.2)
        except pyvisa.Error as err:
            print(err)
        else:
            print('OK')
else:
    print(f'No available {str(list(supported_brands.keys())[0])} brand PSU device found!')
    
