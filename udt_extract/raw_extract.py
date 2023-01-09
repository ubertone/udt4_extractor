# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# author: Marie Burckbuchler

from datetime import datetime  # pour time count

from .ubt_raw_file import ubt_raw_file
from .ubt_raw_config import (
    ubt_raw_config,
    paramus_rawdict2ormdict,
)
from .ubt_raw_data import ubt_raw_data
from .ubt_raw_flag import (
    ANS_TCP_CONFIG,
    ANS_TCP_PROFILE_INST,
    ANS_TCP_MEAS_TEMP,
    ANS_TCP_GAIN_AUTO
)

# for dev:
from struct import calcsize, unpack

def ubt_raw_gain_auto (size, data):
    """Function extracting gain auto chunk

    Args:
        _size (int) : la taille du bloc
        _data : le bloc de données binaire
    Return:
        a0 (float) : intercept of gain auto (dB)
        a1 (float) : slope of gain auto (dB/m)
        ref (int) : configuration reference
    """
    #print("===========detected gain value")
    #print(size, data)
    if size == 16:
        try:
            ref, nb_param, a0, a1 = unpack('iiff', data)  # to check
        except:
            print("struct error : ap_protocol_error(122, \"unexpected chunk content\")")
            raise
        #print("...ANS_TCP_GAIN_AUTO : %d %d %f %f"%(ref, nb_param, a0, a1))
        return ref, a0, a1
    else:
        print("...ANS_TCP_GAIN_AUTO error - ap_protocol_error(122, \"unexpected error when getting gain\")")
        raise

def raw_extract(raw_filename):
    raw_file = ubt_raw_file(raw_filename)

    configs = {}
    i_prof = 0

    try:
        i_config = 1
        while 1:
            flag, size, data = raw_file.read_chunk()
            if flag == ANS_TCP_CONFIG:
                config = ubt_raw_config(raw_file.version)
                config.extract_config(size, data)
                configs["num" + str(i_config)] = config.list_elem
                # c'est avec list_elem['tr_disposition'] qu'il faut décider d'ajouter des clés receivers dans param_us
                #print("settings config num%d: %s"% (i_config, configs["num" + str(i_config)]))
                i_config = i_config + 1
                # todo gérer empty config

            if flag == ANS_TCP_PROFILE_INST:
                # print("detected inst profile")

                if i_prof == 0:
                    print(configs)
                    param_us_dicts = paramus_rawdict2ormdict(configs)
                    #print(param_us_dicts)
                    # ubt_data = ubt_raw_data(configs_hw)
                    ubt_data = ubt_raw_data(param_us_dicts, raw_file.version)
                i_prof += 1

                ubt_data.read_inst_line(size, data)
                # print(ubt_data.data_us_dicts[ubt_data.current_config][ubt_data.current_channel]["snr_doppler_profile"]["data"])

                if i_prof == 1:
                    time_begin = ubt_data.data_us_dicts[ubt_data.current_config][ubt_data.current_channels[0]][
                        list(ubt_data.data_us_dicts[ubt_data.current_config][
                                ubt_data.current_channels[0]].keys())[0]]["time"][0]

            if flag == ANS_TCP_GAIN_AUTO:
                ref, a0, a1 = ubt_raw_gain_auto(size, data)
                for key, config in configs.items():
                    if "ref_config" in config:
                        if config["ref_config"] == ref:
                            current_time = ubt_data.data_us_dicts[ubt_data.current_config][ubt_data.current_channels[0]][
                                list(ubt_data.data_us_dicts[ubt_data.current_config][
                                        ubt_data.current_channels[0]].keys())[0]]["time"][-1]
                            for channel in ubt_data.data_us_dicts[int(key[3:])].keys():
                                for param in ["a0", "a1"]:
                                    if ("param_"+param) not in ubt_data.data_us_dicts[int(key[3:])][channel]:
                                        ubt_data.data_us_dicts[int(key[3:])][channel]["param_"+param] = {"time":[],"data":[]}
                                    ubt_data.data_us_dicts[int(key[3:])][channel]["param_"+param]["time"].append(current_time)
                                ubt_data.data_us_dicts[int(key[3:])][channel]["param_a0"]["data"].append(a0)
                                ubt_data.data_us_dicts[int(key[3:])][channel]["param_a1"]["data"].append(a1)
                    else: # cas UDT001 par exemple
                        # TODO mb 01/10/2021: déterminer ce qu'est la valeur ref dans ce cas
                        # en attendant, on considère que cette valeur correspond au current_config
                        current_time = ubt_data.data_us_dicts[ubt_data.current_config][ubt_data.current_channels[0]][
                            list(ubt_data.data_us_dicts[ubt_data.current_config][
                                    ubt_data.current_channels[0]].keys())[0]]["time"][-1]
                        for channel in ubt_data.data_us_dicts[ubt_data.current_config].keys():
                            for param in ["a0", "a1"]:
                                if ("param_" + param) not in ubt_data.data_us_dicts[ubt_data.current_config][channel]:
                                    ubt_data.data_us_dicts[ubt_data.current_config][channel]["param_" + param] = {"time": [],
                                                                                                    "data": []}
                                ubt_data.data_us_dicts[ubt_data.current_config][channel]["param_" + param]["time"].append(current_time)
                            ubt_data.data_us_dicts[ubt_data.current_config][channel]["param_a0"]["data"].append(a0)
                            ubt_data.data_us_dicts[ubt_data.current_config][channel]["param_a1"]["data"].append(a1)

            if flag == ANS_TCP_MEAS_TEMP:
                print("==========detected temperature value")

    except EOFError:
        print("End of file")
    except:
        print("Error")

    print("%d profiles read" % i_prof)

    if i_prof:
        time_end = ubt_data.data_us_dicts[ubt_data.current_config][ubt_data.current_channels[0]][
            list(ubt_data.data_us_dicts[ubt_data.current_config][
                    ubt_data.current_channels[0]].keys())[0]]["time"][-1]

    return (
        "unknown",
        time_begin,
        time_end,
        param_us_dicts,
        ubt_data.data_us_dicts,
        {},
        configs,
    )