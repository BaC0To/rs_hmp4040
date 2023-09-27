from pyvisa_nge100 import PowerSupply


if __name__ == "__main__":

    psu_settings : dict = {
        'channel': 1,
        'voltage' : 23.99,
        'over_voltage_value' : 25,
        'over_voltage_type' : 'PROTected',
        'current' : 0.2,
        'fuse_trip_time': 0.25 #secs
        }

    psu1 = PowerSupply('ROHDE&SCHWARZ')
    psu1.identification_psu()

    psu1.reset_psu()
    psu1.set_overvoltage_protection(
        True,
        psu_settings.get('over_voltage_type'),
        psu_settings.get('over_voltage_value')
        )
    psu1.set_fuse(True,psu_settings.get('fuse_trip_time'))

    psu1.select_channel(psu_settings.get('channel'))
    psu1.set_channel_params(psu_settings.get('voltage'), psu_settings.get('current'))
    psu1.get_state_psu()
    psu1.set_local_mode()
    