
import logging
import os
import sys
from tempfile import gettempdir
import pyvisa
import serial.tools.list_ports


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


    def __init__(self, brand:str, connection:str) -> None:
        self.vendor_id = self.supported_brands.get(brand.upper())
        self.channel = None
        self.connection = connection
        self.channel_list = [1, 2]
        self.state = None
        self.voltage = None
        self.current = None
        self.result = None
        self.mode = None
        self.value = None
        instr_index = None
        rm = pyvisa.ResourceManager()
        instr_list_available = []

        if self.connection == 'VCP':
            for port in serial.tools.list_ports.comports():
                try:
                    hex_vid = f"{port.vid:#0{6}x}"
                    values = self.supported_brands.get(brand.upper())
                    #if comport connected device vendor equals to supported
                    if values.upper() == hex_vid.upper():
                    # get COM port by searching in the description
                        com_port = port.description[port.description.rfind('(')+1:(len(port.description)-1)]
                        instr_list_available.append(com_port)
                    else:
                        pass
                except TypeError:
                    pass

            for i, instrument in enumerate(instr_list_available):
                instr_index = i

        elif self.connection == 'TMC':
            instr_list = rm.list_resources()
            for i, instrument in enumerate(instr_list):
                if instrument.find(self.supported_brands.get(brand.upper())) != -1 :
                    instr_list_available.append(instrument)
                    instr_index = i


        try:
            self.nge100 = rm.open_resource(instr_list_available[instr_index])
            self.nge100.write('*RST')
        except TypeError :
            logger.error('No available R&S brand PSU device found!')
            sys.exit(-1)



    def __del__(self):
        logging.shutdown()
        #os.remove(tmp_log)

    def identification_psu(self):
        if self.idn is None:
            idn = self.nge100.query('*IDN?').strip()
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
            volt_prot_active = self.nge100.query('VOLTage:PROTection:MODE?').strip()
            volt_prot_value = float(self.nge100.query('VOLT:PROT:LEV?').strip())
            logging.info(f"Channel {channel}: Volt: {voltage}[V], Curr: {current}[A] "
                         f"Output: {output_status}, Meas_Curr: {current_measured}[A] "
                         f"OVP_Type: {volt_prot_active}, OVP_State: {volt_prot} "
                         f"OVP_Value: {volt_prot_value} [V]"
                         )



    def reset_psu(self):
        self.nge100.write('*RST')
        self.nge100.write('SYSTem:LOCal')

    def select_channel(self, channel:int):
        self.channel = channel
        self.nge100.write(f'INSTrument:NSELect {channel}')
        result = self.nge100.query('INSTrument:NSELect?').strip()
        self.result = result
        if int(self.result) != int(self.channel):
            logger.error(f'Requested channel: {result} not selected!')
        return self.result

    def set_channel_params(self, voltage:float, current:float, state:str):
        self.state = state
        self.voltage = voltage
        self.current = current
        self.nge100.write(f'APPLY "{self.voltage},{self.current}"')
        result = self.nge100.query('APPLY?').strip()
        self.result = result
        result_voltage, result_current = result.split(',')
        result_voltage = result_voltage.replace('"', '')
        result_current = result_current.replace('"', '')
        result_current = result_current.strip()
        self.nge100.write(f'OUTPut:SELect {self.state}')
        read_output_state_bool = self.nge100.query('OUTP:SEL?').strip()
        read_output_state_str = 'ON' if read_output_state_bool == '1' else 'OFF'
        if (float(result_voltage) != float(self.voltage) or
                float(result_current) != float(self.current) or
                read_output_state_str != self.state):
            logger.error('Requested channel parameters not accepted by PSU!')
        return self.result

    def enable_master_output(self, state:str):
        self.state = state
        self.nge100.write(f'OUTPut:GENeral {self.state}')
        read_output_master_state_bool = self.nge100.query('OUTPut:GENeral?').strip()
        read_output_state_str = 'ON' if read_output_master_state_bool == '1' else 'OFF'
        if read_output_state_str != self.state:
            logger.error('Requested master output parameter not accepted by PSU!')

    def set_channel_overvoltage_protection(self, value:float, mode:str, state:str):
        self.value = value
        self.mode = mode
        self.state = state
        self.nge100.write(f'VOLT:PROT {self.state}')
        result_state_bool = self.nge100.query('VOLT:PROT?').strip()
        result_state_str = 'ON' if result_state_bool == '1' else 'OFF'
        self.nge100.write(f'VOLT:PROT:MODE {self.mode}')
        result_mode = self.nge100.query('VOLT:PROT:MODE?').strip()
        self.nge100.write(f'VOLT:PROT:LEV {self.value}')
        result_value = self.nge100.query('VOLT:PROT:LEV?').strip()
        if (result_state_str != self.state or result_mode != self.mode or
            float(result_value) != float(self.value)):
            logger.error('Requested OVP channel parameters not accepted by PSU unit!')


    def set_channel_fuse(self, value:float, state:str):
        self.value = value
        self.state = state
        self.nge100.write(f'FUSE {self.state}')
        result_state_bool = self.nge100.query('FUSE?').strip()
        result_state_str = 'ON' if result_state_bool == '1' else 'OFF'
        self.nge100.write(f'FUSE:DEL {self.value}')
        result_value = self.nge100.query('FUSE:DEL?').strip()
        if (result_state_str != self.state or float(result_value) != float(self.value)):
            logger.error('Requested FUSE channel parameters not accepted by PSU unit!')

    def set_local_remote_mode(self, mode:str):
        self.mode = mode
        if self.mode == 'LOCAL':
            self.nge100.write('SYSTem:LOCal')
        else:
            self.nge100.write('SYSTem:REMote')
