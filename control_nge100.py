
"""
This module controls a R&S NGE100 PSU

Attributes:
    JSON_FILENAME (str): A .json filename that corresponds to the PSU config
    file name

Todo:
    * ????
    * ????
"""
from pyvisa_nge100 import PowerSupply
from read_json_settings import read_nge100_config_from_json

JSON_FILENAME = 'nge100_settings.json'

#if __name__ == "__main__":

psu_json_settings = read_nge100_config_from_json(JSON_FILENAME)

psu1 = PowerSupply('ROHDE&SCHWARZ','VCP')
psu1.identification_psu()
psu1.reset_psu()
for idx, settings in enumerate(psu_json_settings):
    if idx != 0:
        #set channel settings
        psu1.select_channel(idx)
        psu1.set_channel_overvoltage_protection(settings.get('over_voltage_value'),
                                                settings.get('over_voltage_mode'),
                                                settings.get('over_voltage_state')
                                                )
        psu1.set_channel_fuse(settings.get('fuse_trip_time'),
                                settings.get('fuse_state')
                                )
        psu1.set_channel_params(settings.get('voltage'),
                                settings.get('current'), settings.get('state')
                                )
    else:
        #set common settings
        psu1.enable_master_output(settings.get('state'))
psu1.get_state_psu()
psu1.set_local_remote_mode('REMOTE')
psu1.reset_psu()
