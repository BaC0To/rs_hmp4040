"""
This module reads the R&S nge100 power supply parameters from a .json
config file


Attributes:
    JSON_FILENAME (str): Filename of the config file

"""
import json
import os
from pathlib import Path
JSON_FILENAME = 'nge100_settings.json'

def read_nge100_config_from_json(filename:str):
    """
        This function reads all the settings of the PSU per channel

        Args:
            filename (str): The config file filename.

        Returns:
            psu_settings_list (list) : PSU settings per channel

        Raises:
            ValueError: If .json config file not present
    """
    #psu_settings_list = []
    try:
        with open(Path(os.path.join(os.getcwd(), 'config_files',filename)), 'r',
                  encoding="utf-8") as file:
            json_data = json.load(file)
            # loop over channels
            # for psu_channel in json_data:
            #     print(psu_channel)
            #     #channel N data -->
            #     for ch_settings in json_data[psu_channel]:
            #         psu_settings_list.append(ch_settings)
        #return psu_settings_list
        return json_data
    except IOError as exc:
        raise ValueError('File not found!') from exc
