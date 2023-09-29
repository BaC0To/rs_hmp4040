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

psu_settings_json = read_nge100_config_from_json(JSON_FILENAME)
psu1 = PowerSupply('ROHDE&SCHWARZ','VCP')
psu1.identification_psu()
#psu1.reset_psu()
for idx, settings in enumerate(psu_settings_json):
    if settings != 'common':
        #set channel settings
        psu1.select_channel(settings)
        psu1.set_channel_fuse(psu_settings_json.get(settings).get('fuse_trip_time'),
                            psu_settings_json.get(settings).get('fuse_state')
                            )
        psu1.set_channel_ovp(psu_settings_json.get(settings).get('over_voltage_value'),
                            psu_settings_json.get(settings).get('over_voltage_mode'),
                            )
        psu1.set_channel_params(psu_settings_json.get(settings).get('voltage'),
                                psu_settings_json.get(settings).get('current'),
                                psu_settings_json.get(settings).get('state')
                                )
        psu1.get_state_channel(settings)

psu1.enable_master_output(psu_settings_json.get('common').get('state'))
psu1.error_checks()
psu1.set_local_remote_mode('LOCAL')
#psu1.reset_psu()
