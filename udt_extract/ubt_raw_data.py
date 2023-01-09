# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

from struct import calcsize, unpack
from numpy import asarray as ar
import numpy as np

from .ubt_time_ref import ub_time_t
from .date_parser import date_parse

class ubt_raw_data():
    def __init__(self, param_us_dicts, udt_version):
        # liste des dictionnaires standardisés des données non US (model Measure)
        self.data_dicts = {}
        # dict, ordonné par num_config, channel_id, de listes des dictionnaires standardisés des données US (model MeasureUs)
        self.data_us_dicts = {}
        self.param_us_dicts = param_us_dicts
        for config in self.param_us_dicts.keys():
            self.data_us_dicts[config] = {}
            for channel in self.param_us_dicts[config].keys():
                self.data_us_dicts[config][channel] = {}
                for datatype in ["echo_profile", "echo_sat_profile", "velocity_profile", "snr_doppler_profile"]:
                    self.data_us_dicts[config][channel][datatype] = {"time": [], "data": []}
        self.current_config = None
        self.current_channels = None

        self.udt_version = udt_version

    def read_inst_line(self, size, data):
        if int(self.udt_version[3:]) > 1 and int(self.udt_version[3:]) < 5:
            head_size = calcsize('iIIii')
            ref, size_data, size_raw, sec, n_sec = unpack('iIIii', data[0:head_size])
            #print("header :", ref, size_data, size_raw, sec, n_sec)
        elif int(self.udt_version[3:]) == 1:
            head_size = calcsize('iiiiff')
            n_vol, ref, sec, n_sec, origine, interval = unpack('iiiiff', data[0:head_size])
            size_data = (2 * calcsize('f') + calcsize('i')) * n_vol
            #print("header :", n_vol, ref, sec, n_sec, origine, interval)
        else:
            print("unknown version")
            raise
        # todo gérer empty profile
        # ref_config = (ref&0xFFFFFF00)>>8
        self.current_config = ref & 0x000000FF
        self.current_channels = list(self.param_us_dicts[self.current_config].keys())

        if self.current_config not in self.data_us_dicts.keys():
            raise Exception('chunk', "unexpected number of configurations (%d)" % self.current_config)

        time = date_parse(ub_time_t(sec, n_sec).as_datetime().strftime("%Y-%m-%dT%H:%M:%S.%f"))

        ###################
        # vectors reading
        ###################
        vectors_dict = {
            "velocity": [],
            "variance": [],
            "qualite": [],
        }

        offset = head_size
        tab_size = int(size_data / 3)
        nb_total_vol = 0
        # print(self.current_channels)
        for channel in self.current_channels:
            nb_total_vol = nb_total_vol + self.param_us_dicts[self.current_config][channel]["n_cell"]
        #print("profiles size: %s" % calcsize('%df%df%di' % (nb_total_vol, nb_total_vol, nb_total_vol)))
        #print("data slice size: %s" % len(data[offset: offset + nb_total_vol * 3 * tab_size]))
        #print("size_data in header: %s" % size_data)
        unpacked_data = ar(unpack('%df%df%di' % (nb_total_vol, nb_total_vol, nb_total_vol),
                                  data[offset: offset + nb_total_vol * 3 * tab_size]))
        vectors_dict['velocity'] = unpacked_data[0:nb_total_vol]
        vectors_dict['amplitude'] = unpacked_data[nb_total_vol:2 * nb_total_vol]
        vectors_dict['qualite'] = unpacked_data[2 * nb_total_vol:3 * nb_total_vol].astype(np.int64)

        self.conversion_profile(vectors_dict)

        ###################################################################################################
        # rangement dans la liste de dictionnaires de données US (ici tous les profils sont des données US)
        ###################################################################################################
        offset = 0
        for channel in self.current_channels:
            for datatype in ["echo_profile", "echo_sat_profile", "velocity_profile", "snr_doppler_profile"]:
                self.data_us_dicts[self.current_config][channel][datatype]["time"].append(time)
            self.data_us_dicts[self.current_config][channel]["echo_profile"]["data"].append(
                vectors_dict['amplitude'][offset::len(self.current_channels)])
            self.data_us_dicts[self.current_config][channel]["echo_sat_profile"]["data"].append(
                vectors_dict['sat'][offset::len(self.current_channels)])
            self.data_us_dicts[self.current_config][channel]["velocity_profile"]["data"].append(
                vectors_dict['velocity'][offset::len(self.current_channels)])
            self.data_us_dicts[self.current_config][channel]["snr_doppler_profile"]["data"].append(
                vectors_dict['snr'][offset::len(self.current_channels)])
            offset = offset + 1

    def conversion_profile(self, vectors_dict):
        vectors_dict['amplitude'] = np.sqrt(np.absolute(vectors_dict['amplitude']))
        vectors_dict['snr'] = (((vectors_dict['qualite'] & 0x000000FF).astype(
            float)) * 20.0 / 255.0) - 10.0  # 2013/03/04 Damien : plage SNR : [-10dB +10dB]
        vectors_dict['sat'] = ((vectors_dict['qualite'] >> 8) & 0x000000FF).astype(float)
        vectors_dict['ny_jp'] = ((vectors_dict['qualite'] >> 16) & 0x000000FF).astype(float)
        vectors_dict['sigma'] = ((vectors_dict['qualite'] >> 24) & 0x000000FF).astype(float)
