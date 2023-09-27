from pyvisa_nge100 import PowerSupply


if __name__ == "__main__":

    psu_settings : dict = {
        'channel': 1,
        'voltage' : 23.99,
        'over_voltage' : 25,
        ' over_voltage_type' : 'PROT',
        'current' : 0.2,
        'fuse_trip_time': 0.15
        }

    psu1 = PowerSupply('ROHDE&SCHWARZ')
    psu1.identification_psu()

    psu1.reset_psu()
    psu1.select_channel(psu_settings.get('channel'))
    psu1.set_channel_params(psu_settings.get('voltage'), psu_settings.get('current'))
    psu1.get_state_psu()
