#!/usr/bin/env python3
# -*- coding: UTF_8 -*-
import sys
sys.path.append("..")

from datetime import datetime  # pour time count
from udt_extract.raw_extract import raw_extract

# Path to raw.udt file to extract (from UB-Lab X2, X8, 2C, UB-Flow and UB-Lab S2)
path = "./raw_test_udt001.udt" # "./raw_test_udt001.udt" "./raw_test_udt002.udt"


extract_start = datetime.now()
# Extraction function:
(
    device_name,
    time_begin,
    time_end,
    param_us_dicts,
    data_us_dicts,
    data_dicts,
    settings_dict
) = raw_extract(path)
print(
        "=============\nextract duration:%s\n==========="
        % (datetime.now() - extract_start)
    )
print(device_name)
print(time_begin, time_end)
## Extracted data are arranged in dictionnaries:
# param_us_dicts: 
print("================\nUltrasound (US) measurement parameter\n==================")
print("Configuration numbers available: ", param_us_dicts.keys()) # gives the configuration numbers available in this set of data
first_configuration = list(param_us_dicts.keys())[0] # gives the configuration number of the first available configuration
print("Receiving channels available for one of the configurations: ", param_us_dicts[first_configuration].keys()) # gives the list of receiving channels (transducers) for this first configuration
first_channel = list(param_us_dicts[first_configuration].keys())[0] # gives the channel number of the first available channel for this first configuration
print("US Parameters for one receiving channel of one of the configurations: ", param_us_dicts[first_configuration][first_channel]) # gives the set of parameters used for the measurement of the data associated to this first configuration anad first receiving channel (emission frequency, PRF etc.)

# data_dicts: measured data not measured by ultrasound or not related directly those who ultrasound
print("\n================\nNon Ultrasound (US) measured/recorded data\n==================")
# thus, they are not related to a number of configuration nor a receiving channel
# could be empty if no such data is available or has been recorded
if data_dicts:
    print("Available non US datatypes: ", data_dicts.keys()) # gives the datatypes available for this recording
    first_datatype = list(data_dicts.keys())[0] # one of those datatypes
    print("timestamp list for the first datatype %s: "%first_datatype, data_dicts[first_datatype]["time"]) # gives the list of timestamps associated to the list of values for this datatype
    print("and corresponding data: ", data_dicts[first_datatype]["data"]) # gives the list of values associated to the list of timestamps for this datatype. The values cas be arrays.

# data_us_dicts
print("\n================\nUltrasound (US) measured/recorded data\n==================")
# those are also first arranged by configuration number and receiving channel number
print(data_us_dicts[first_configuration][first_channel].keys()) # gives the US datatypes available for one configuration and one channel
first_us_datatype = list(data_us_dicts[first_configuration][first_channel].keys())[0]
timestamp_first_US_datatype = data_us_dicts[first_configuration][first_channel][first_us_datatype]["time"] # gives the list of timestamps associated to the list of values for this datatype
print("earliest available data: %s\nlastest available data: %s"%(min(timestamp_first_US_datatype),max(timestamp_first_US_datatype)))
corresponding_US_data = data_us_dicts[first_configuration][first_channel][first_us_datatype]["data"] # gives the list of values associated to the list of timestamps for this datatype. The values cas be arrays.
print(len(corresponding_US_data))
