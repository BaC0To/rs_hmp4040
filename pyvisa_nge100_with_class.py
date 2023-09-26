
import pyvisa
#import logging




VENDOR_ID = '0x0AAD' # Rohde & Schwarz VID_0x0AAD


class PowerSupply:

    idn = None
    vendor_id: str
    supported_brands: dict = {
        'ROHDE&SCHWARZ': "0x0AAD"
    }


    def __init__(self, brand:str) -> None:

        self.vendor_id = self.supported_brands.get(brand.upper())
    
    # def __del__(self) -> None:
    #     self.power_supply_unit.write("SYSTem:LOCal")
    #     self.power_supply_unit.close()

    def discover(self):
        
        rm = pyvisa.ResourceManager()
        instr_list = rm.list_resources()
        
        for i, instrument in enumerate(instr_list):
            _index = i if instrument.find(VENDOR_ID) != -1 else _index
        
        resource_string_1 = instr_list[_index]
        
        self.power_supply_unit = rm.open_resource(resource_string_1)

    def identification(self):
        
        if self.idn is None:
            idn = self.power_supply_unit.query('*IDN?')
            manufacturer, device_type, part_sn_number, fw_ver = idn.split(',')
            print(
                "--- PSU details ---\n"
                f"Manufacturer: {manufacturer}\n"
                f"Device_Type: {device_type}\n"
                f"Part_ Number/Serial: {part_sn_number}\n"
                f"FW_Ver: {fw_ver.strip()}"
            )
            self.idn = idn
        return self.idn

    def reset(self):
      
        self.power_supply_unit.write('*RST')


    def select_channel(self, channel:int):
        """
        This function defines the numeric selection of a channel
        
        Args:
            channel(int): The number of the channel.
        
        Asserts:
            None.
            
        Returns:
            None.
        
        Raises:
            ValueError: When .... raises ....

        Examples:
            ....
            >>> from x import y
            >>> y()
        """
        self.channel = channel
        self.power_supply_unit.write(f'INST OUT{self.channel}')
        

    def set_voltage_current(self, voltage:float, current:float):
        
        self.voltage = voltage
        self.current = current
        self.power_supply_unit.write(f'APPLY "{self.voltage},{self.current}"')

    def set_overvoltage_protection(self, state:bool, type:str, value:float):
       
        self.state = state
        self.type = type
        self.value = value

        setting = "ON" if self.state else "OFF"
        self.power_supply_unit.write(f'VOLT:PROT {setting}')
        
        self.power_supply_unit.write(f'VOLT:PROT:MODE {self.type}')
        self.power_supply_unit.write(f'VOLT:PROT:LEV {self.value}')
        


    def set_fuse(self, state:bool, trip_value:int):
        
        self.state = state
        self.trip_value = trip_value

        setting = "ON" if self.state else "OFF"
        self.power_supply_unit.write(f'FUSE {setting}')
        self.power_supply_unit.write(f'FUSE:DEL {self.trip_value}')

    def enable_channel(self, state:bool, channel:int):
        
        self.state = state
        self.channel = channel

        setting = "ON" if self.state else "OFF"
        self.power_supply_unit.write(f'OUTP {setting}')

    def enable_output(self, state:bool):
       
        self.state = state
        
        setting = "ON" if self.state else "OFF"
        self.power_supply_unit.write(f'OUTPut:GENeral {setting}')
    
    def set_local(self, state:bool):

        self.state = state
        if self.state:
            self.power_supply_unit.write('SYSTem:LOCal')


channel = 1
voltage = 24
over_voltage = 25
over_voltage_type = 'PROT'
current = 0.2
fuse_trip_time = 0.15



psu1 = PowerSupply('ROHDE&SCHWARZ')
psu1.discover()
psu1.identification()
psu1.reset()

psu1.select_channel(channel)
psu1.set_voltage_current(voltage, current)
psu1.set_overvoltage_protection(True, 'over_voltage_type', over_voltage)
psu1.set_fuse(True, fuse_trip_time)
psu1.enable_channel(True,channel)
#psu1.enable_output(True)
psu1.set_local(True)

