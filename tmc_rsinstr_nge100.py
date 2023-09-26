


from RsInstrument import RsInstrument
import time

VENDOR_ID = '0x0AAD' # Rohde & Schwarz VID_0x0AAD

instr_list = RsInstrument.list_resources()
print(f'The resource list contains : {instr_list}')

index = 0
counter = 0

for item in instr_list:
    if item.find(VENDOR_ID) != -1:
        index = counter
    counter += 1
        
resource_string_1 = instr_list[index]
instr = RsInstrument(resource_string_1)
idn = instr.query_str('*IDN?')

splitted_idn_string = idn.split(',')
manufacturer, device_type, part_sn_number, fw_ver = splitted_idn_string
print(f'--- PSU details ---\nManufacturer: {manufacturer}\nDevice_Type: {device_type}\nPart_ Number/Serial: {part_sn_number}\nFW_Ver: {fw_ver}')
time.sleep(0.2)
instr.write('*RST')
time.sleep(1)


instr.close()