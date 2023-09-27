
import logging
import os
import pyvisa
import sys
from tempfile import gettempdir


VENDOR_ID = '0x0AAD' # Rohde & Schwarz VID_0x0AAD
LOG_FILE = 'psu.log'

tmp_log = os.path.join(gettempdir(),LOG_FILE)

logging.basicConfig(filename=tmp_log,format='[ %(asctime)s ][ %(levelname)s ]:  %(message)s',
                     datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO
                    )

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

class PowerSupply:


    idn = None
    vendor_id: str
    supported_brands: dict = {
        'ROHDE&SCHWARZ': "0x0AAD"
    }


    def __init__(self, brand:str) -> None:
        self.vendor_id = self.supported_brands.get(brand.upper())
        self.channel_list = [1, 2]
        instr_index = None
        instr_list_available = []
        rm = pyvisa.ResourceManager()
        instr_list = rm.list_resources()
        for i, instrument in enumerate(instr_list):
            if instrument.find(VENDOR_ID) != -1 :
                instr_list_available.append(instrument)
                instr_index = i

        try:
            self.nge100 = rm.open_resource(instr_list_available[instr_index])
            #self.nge100.write('*RST')
        except TypeError :
            logger.error('No available R&S brand PSU device found!')
            sys.exit(-1)

    def __del__(self):
        logging.shutdown()
        #os.remove(tmp_log)
        print('Destructor called')


    def identification_psu(self):
        if self.idn is None:
            idn = self.nge100.query('*IDN?')
            self.idn = idn
            logging.info(idn)
        return self.idn

    def get_state_psu(self):
        """
        This function returns all the settings of the PSU per channel
        
        Args:
            None.
                    
        Returns:
            {
                'voltage': float , set voltage,
                'current': float , set urrent,
                'status': int , status,
                'current_measured': float , measured real current,
                'volt_prot': float , voltage protection value,
                'volt_prot_active': str , voltage protection mode
            }
        """
        for channel in self.channel_list:
            self.nge100.write(f'INSTrument:NSELect {channel}')
            voltage = float(self.nge100.query('SOURce:VOLTage?'))
            current = float(self.nge100.query('SOURce:CURRent?'))
            output_status = int(self.nge100.query('OUTPut:STATe?'))
            current_measured = float(self.nge100.query('MEASure:CURRent?'))
            volt_prot = float(self.nge100.query('VOLTage:PROTection?'))
            volt_prot_active = self.nge100.query('VOLTage:PROTection:MODE?').rstrip('\r\n')
            logging.info(f"Channel {channel}: Volt: {voltage}[V], Curr: {current}[A] "
                         f"Output: {output_status}, Meas_Curr: {current_measured}[A] "
                         f"OVP_Type: {volt_prot_active}, OVP_Value: {volt_prot}"                      
                         )



    def reset_psu(self):
        self.nge100.write('*RST')
        self.nge100.write('SYSTem:LOCal')
    
    def select_channel(self, channel:int):
        self.channel = channel
        self.nge100.write(f'INSTrument:NSELect {channel}')
        result = self.nge100.query('INSTrument:NSELect?').rstrip('\n')
        self.result = result
        if int(self.result) != int(self.channel):
            logger.error(f'Requested Channel: {result} not selected!')
        return self.result
    
    def set_channel_params(self, voltage:float, current:float):
        self.voltage = voltage
        self.current = current
        self.nge100.write(f'APPLY "{self.voltage},{self.current}"')
        result = self.nge100.query('APPLY?').rstrip('\n')
        self.result = result
        result_voltage, result_current = result.split(',')
        result_voltage = result_voltage.replace('"', '')
        result_current = result_current.replace('"', '')
        result_current = result_current.strip()
        print(result_voltage)
        print(result_current)
        if float(result_voltage) == self.voltage or result_current != self.current:
            logger.error(f'Requested Parameters: ')
        return self.result

    def set_overvoltage_protection(self, state:bool, type:str, value:float):
        self.state = state
        self.type = type
        self.value = value

        setting = "ON" if self.state else "OFF"
        self.nge100.write(f'VOLT:PROT {setting}')
        self.nge100.write(f'VOLT:PROT:MODE {self.type}')
        self.nge100.write(f'VOLT:PROT:LEV {self.value}')
        
    def set_fuse(self, state:bool, trip_value:int):
        self.state = state
        self.trip_value = trip_value
        setting = "ON" if self.state else "OFF"
        self.nge100.write(f'FUSE {setting}')
        self.nge100.write(f'FUSE:DEL {self.trip_value}')

    def enable_channel(self, state:bool, channel:int):
        self.state = state
        self.channel = channel
        setting = "ON" if self.state else "OFF"
        self.nge100.write(f'OUTP {setting}')

    def enable_output(self, state:bool):
        self.state = state
        setting = "ON" if self.state else "OFF"
        self.nge100.write(f'OUTPut:GENeral {setting}')
