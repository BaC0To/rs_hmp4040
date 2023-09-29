import logging
import os
import sys
from tempfile import gettempdir
import re
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
        self.channel_number = None
        self.state = None
        self.voltage = None
        self.current = None
        self.result = None
        self.mode = None
        self.value = None
        instr_index = None
        self.error = None
        rm = pyvisa.ResourceManager()
        instr_list_available = []

        if self.connection == 'VCP':
            for port in serial.tools.list_ports.comports():
                try:
                    hex_vid = f"{port.vid:#0{6}x}"
                    values = self.supported_brands.get(brand.upper())
                    #if comport connected device vendor equals to supported
                    if values.upper() == hex_vid.upper():
                    # get COM port by reverse earching in the description for data COMx
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
            #self.nge100.write('*RST')
        except TypeError :
            logger.error('No available R&S brand PSU device found!')
            sys.exit(-1)



    def __del__(self):
        logging.shutdown()
        #os.remove(tmp_log)

    def identification_psu(self):
        """
        This function sends IDN command and r
        eturns the instrument identification.

        Args:
            None.

        Returns:
            self.idn (str): instrument identification.
        """
        if self.idn is None:
            idn = self.nge100.query('*IDN?').strip()
            self.idn = idn
            logging.info(idn)
        return self.idn

    def get_state_channel(self, channel:str):
        """
        This function returns all the settings of the PSU per channel

        Args:
            chenanel (str): Active selected channel number

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
        self.channel = channel
        temp = re.findall(r'\d+',  self.channel)
        res = list(map(int, temp))
        channel_number = int(res[0])
        self.nge100.write(f'INSTrument:NSELect {channel_number}')
        voltage = float(self.nge100.query('SOURce:VOLTage?'))
        current = float(self.nge100.query('SOURce:CURRent?'))
        output_status = int(self.nge100.query('OUTPut:STATe?'))
        current_measured = float(self.nge100.query('MEASure:CURRent?'))
        volt_prot_state = '1' if float(self.nge100.query('VOLTage:PROTection?'))!= 0 else '0'
        volt_prot_mode = self.nge100.query('VOLTage:PROTection:MODE?').strip()
        volt_prot_value = float(self.nge100.query('VOLT:PROT:LEV?').strip())
        ch_fuse_state = self.nge100.query('FUSE?').strip()
        ch_fuse_value = self.nge100.query('FUSE:DEL?').strip()
        logging.info("Channel %s: Volt: %s [V],Curr: %s [A],"
                        "Out_Stat: %s,Meas_Curr: %s [A],"
                        "OVP_Stat: %s,OVP_Type: %s,"
                        "OVP_Val: %s [V],"
                        "FUSE_Stat: %s,FUSE_Val: %s [msec]",
                        channel_number, voltage, current, output_status,
                        current_measured, volt_prot_state, volt_prot_mode.upper(), volt_prot_value,
                        ch_fuse_state, ch_fuse_value
                        )


    def reset_psu(self):
        """
        This function resets the PSU

        Args:
            None.

        Returns:
            None.
        """
        self.nge100.write('*RST')
        self.nge100.write('SYSTem:LOCal')

    def select_channel(self, channel:int):
        """
        This function selects the PSU physical channel

        Args:
            channel (str): current selection

        Returns:
            result (str): selected channel
        """
        self.channel = channel
        temp = re.findall(r'\d+',  self.channel)
        res = list(map(int, temp))
        channel_number = int(res[0])
        self.nge100.write(f'INSTrument:NSELect {channel_number}')
        result = int(self.nge100.query('INSTrument:NSELect?').strip())
        self.result = result
        if self.result != channel_number:
            logger.error('Requested channel: %s not selected!', channel_number)
        return self.result

    def set_channel_params(self, voltage:float, current:float, state:str):
        """
        This function sets the selected PSU channel's settings : voltage
        current and output state

        Args:
            voltage (float): to set voltage [V]
            current (float): to set current [A]
            state (str): ON/OFF to activate or deactivate this option

        Returns:
            self.result
        """
        self.state = state
        self.voltage = voltage
        self.current = current
        self.nge100.write(f'VOLT {voltage}')
        result_voltage = float(self.nge100.query('VOLT?').strip())
        self.nge100.write(f'CURR {current}')
        result_current = float(self.nge100.query('CURR?').strip())
        self.nge100.write(f'OUTPut:SELect {self.state}')
        read_output_state_bool = self.nge100.query('OUTP:SEL?').strip()
        read_output_state_str = 'ON' if read_output_state_bool == '1' else 'OFF'
        if (result_voltage != voltage or result_current != current or
            read_output_state_str != self.state):
            logger.error('Requested channel parameters %s [V], %s [A] not accepted by PSU!',
                         voltage, current
                         )
        result = str(result_voltage)+", "+str(result_current)
        self.result = result
        return self.result

    def enable_master_output(self, state:str):
        """
        This function sets the master output ON/OFF

        Args:
        state (str): ['ON'|'OFF'] to activate or deactivate this option

        Returns:
        None.
        """
        self.state = state
        self.nge100.write(f'OUTPut:GENeral {self.state}')
        read_output_master_state_bool = self.nge100.query('OUTPut:GENeral?').strip()
        read_output_state_str = 'ON' if read_output_master_state_bool == '1' else 'OFF'
        if read_output_state_str != self.state:
            logger.error('Requested master output command not accepted by PSU!')

    def set_channel_ovp(self, value:float, mode:str):
        """
        This function sets the channel ovp protection

        Args:
            value (float): The selected threshold value in [V]
            mode (str):MEASured --> The OVP switches off if the measured value exceeds.
                        PROTected If the adjusted threshold is exceeded the output;
                        additionally the measured value is monitored.
            state (str): ON/OFF to activate or deactivate this option

        Returns:
            result (str): Actual settings for OVP of selected channel
        """
        self.value = value
        self.mode = mode
        self.nge100.write(f'VOLT:PROT:LEV {value}')
        result_value = float(self.nge100.query('VOLT:PROT:LEV?'))
        #result_state_str = self.nge100.query('VOLT:PROT?').strip()
        self.nge100.write(f'VOLT:PROT:MODE {mode}')
        result_mode = self.nge100.query('VOLT:PROT:MODE?').strip().upper()
        if (result_value != value or result_mode != mode.upper()):
            logger.error("Requested OVP channel parameters %s [V], Mode: %s "
                        "not accepted by PSU unit!",value, mode)
        result = str(result_value) + ", "+ result_mode
        self.result = result
        return self.result

    def set_channel_fuse(self, value:int, state:str):
        """
        This function sets the channel ovc fuse current protection

        Args:
            value (int): The selected time in msec after the fuse is tripped
            state (str): ON/OFF to activate or deactivate this option

        Returns:
            result (str). Actual set parameters for fuse settings per channel
        """
        self.value = value
        self.state = state
        if self.state == 'ON':
            self.nge100.write(f'FUSE:DEL {value}')
            result_value = int(self.nge100.query('FUSE:DEL?').strip())
            self.nge100.write(f'FUSE {state}')
            result_state_str = self.nge100.query('FUSE?').strip()
            result_state= 'ON' if result_state_str == '1' else 'OFF'
            if (result_value != value or result_state != state):
                logger.error("Requested FUSE channel parameters %s [sec] "
                            "not accepted by PSU unit!", value)
            result = result_state + ", " + str(result_value)
        else:
            result = state
        self.result = result
        return self.result

    def set_local_remote_mode(self, mode:str):
        """
        This function sets the system to remote / front panel control or
        a more secure rwlock where the unit unlocks only by a command 'LOCAL'
        or by a RST

        Args:
            mode (str): The selected mode [cLOCAL'|'REMOTE'|'RWLOCK']

        Returns:
            None.
        """
        self.mode = mode
        if self.mode == 'REMOTE':
            self.nge100.write('SYSTem:REMote')
        elif self.mode == 'RWLOCK':
            self.nge100.write('SYSTem:RWLock')
        else:
            self.nge100.write('SYSTem:LOCal')

    def error_checks(self):
        """
        This is an errock check function

        Args:
            None.

        Returns:
            my_errror (list): A list of errors if present
        """
        my_error = []
        error_list = self.nge100.query('SYSTem:ERRor?').split(',')
        error = error_list[0]
        if int(error) == 0:
            logging.info('No error!')
        else:
            while int(error)!=0:
                logger.error("error #: %s", error_list[0])
                logger.error("error Description: %s", error_list[1])
                my_error.append(error_list[0])
                my_error.append(error_list[1])
                error_list = self.nge100.query("SYST:ERR?").split(',')
                error = error_list[0]
                my_error = list(my_error)
                self.error = my_error
        return my_error
