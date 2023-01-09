# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

from .convert_type import translate_paramdict

from struct import calcsize, unpack

def paramus_rawdict2ormdict(settings_dict):
    """Function that converts a settings dict read from a raw file (webui2, UB-Lab P) to a formatted dict for data processing.

    Args:
        settings_dict (dict): original settings dict in raw.udt file

    Returns:
        paramus (dict): dict structure with keys the config int, with subkey the channel int and value the paramus dict
    """
    # dict of config parameters of channel_id of config_id in this settings dict
    paramus = {}

    # keep order of configuration_order:
    for config_num in settings_dict.keys():
        paramus[int(config_num[-1])] = {}
        temp_param = settings_dict[config_num]
        # clean subdicts parts:
        if 'n_subvol' in settings_dict[config_num]:
            # c'est le cas HSR qu'on cherche, et hors bistatique, car pour bistatique n_vol est la ref et n_subvol=2.
            if settings_dict[config_num]['n_vol'] == 1 and settings_dict[config_num]['n_subvol'] > 2:
                if ('tr_disposition' in settings_dict[config_num]):
                    if settings_dict[config_num]['tr_disposition'] == 1:
                        temp_param['n_vol'] = int(temp_param['n_subvol'] / 2.)
                    else:
                        temp_param['n_vol'] = temp_param['n_subvol']
                temp_param['r_dvol'] = temp_param['r_dsubvol']
        
        if "auto_gain_a0" in temp_param.keys():
            if temp_param["auto_gain_a0"]:
                if "gain_a0" in temp_param.keys():
                    del temp_param["gain_a0"]
                if "gain_a1" in temp_param.keys():
                    del temp_param["gain_a1"]

        key2delete = []
        item2add = {}
        for key, elem in temp_param.items():
            if isinstance(elem, dict):
                print("type dict detected for key: %s" % key)
                for param_key, param_elem in elem.items():
                    item2add[param_key] = param_elem
                key2delete.append(key)
        for key in key2delete:
            del temp_param[key]
        for key, elem in item2add.items():
            temp_param[key] = elem

        # translate for orm param names:
        temp_param = translate_paramdict(temp_param)

        # add global settings elements:
        # temp_param["operator"] = settings_dict["global"]["operator"]
        # temp_param["comments"] = settings_dict["global"]["comments"]
        # temp_param["sound_speed"] = settings_dict["global"]["sound_speed"]["value"]

        # translate for unique format with dict cleaner and with formated dict:
        # paramus.append({"config_id":int(config_num[-1]), "channel_id":int(temp_param["emitter"][2:]), "data":temp_param})
        if isinstance(temp_param["receiver"], int):
            tr = temp_param["receiver"]  # dans raw apf02, c'est directement un int
        else:
            tr = int(temp_param["receiver"][2:])  # dans raw webui2, c'est un string "tr%d"
        paramus[int(config_num[-1])][tr] = dict(temp_param)

        # gestion du cas multi-receiver, actuellement seulement bistatique dans raw apf02:
        if "tr_disposition" in settings_dict[config_num]:
            print("WEBUI1 settings with tr_disposition")
            if settings_dict[config_num]["tr_disposition"] == 1:
                paramus[int(config_num[-1])][tr + 1] = dict(temp_param)
                paramus[int(config_num[-1])][tr + 1]["receiver"] = tr + 1

    return paramus

class ubt_raw_config():
    def __init__(self, _data_format=None):
        self.data_format = _data_format
        self.data_type_c = {}
        for data_name in ['method', 'tr_out', 'tr_disposition', 'n_vol', 'n_subvol', 'n_ech', 'n_profil',
                          'auto_gain_a1', 'auto_gain_a0']:
            self.data_type_c[data_name] = 'i'
        for data_name in ['f0', 'prf', 'r_vol1', 'r_dvol', 'r_dsubvol', 'r_em', 'moving_avr', 'gain_a0', 'gain_a1',
                          'R_Ny', 'sound_speed']:
            self.data_type_c[data_name] = 'f'
        # tr_disposition some times was called ch_in

        # params in bool_value:
        for data_name in ['phase_coding', 'static_echo_filter', 'IQ_tatency', 'V_em']:
            self.data_type_c[data_name] = 'i'

        if _data_format is None:
            print("Warning, please specify data format for the settings")
            return

        if _data_format == "UDT001":
            self.data_type_c['v_min'] = 'f'
            self.data_type_c['phase_coding'] = 'B'
            self.data_type_c['static_echo_filter'] = 'B'
            self.data_type_c['d0'] = "h"

            self.param_order = ["method", "v_min", "tr_out", "tr_disposition", "f0", "prf", "r_vol1", "r_dvol"]

            self.po_follow_1 = ["n_vol", "r_em", "n_ech", "phase_coding", "static_echo_filter", "d0", "n_profil",
                                "moving_avr", "auto_gain_a0", "gain_a0", "gain_a1"]
            self.po_follow_2 = ["n_vol", "r_em", "n_ech", "phase_coding", "static_echo_filter", "d0", "n_profil",
                                "moving_avr", "auto_gain_a0", "gain_a0", "auto_gain_a1", "gain_a1"]
            self.po_follow_3 = ["r_dsubvol", "n_vol", "n_subvol", "r_em", "n_ech", "phase_coding", "static_echo_filter",
                                "d0", "n_profil", "moving_avr", "gain_a0", "auto_gain_a0", "gain_a1", "auto_gain_a1",
                                "R_Ny"]

        elif _data_format == "UDT002":
            self.data_type_c['phase_coding'] = 'h'
            self.data_type_c['static_echo_filter'] = 'h'
            # TODO, voir si phase coding et SEF ne sont pas comme pour le data_format 1
            self.data_type_c['v_min'] = 'f'
            self.param_order = ["method", "v_min", "tr_out", "tr_disposition", "f0", "prf", "r_vol1", "r_dvol",
                                "r_dsubvol", "n_vol", "n_subvol", "r_em", "n_ech", "phase_coding", "static_echo_filter",
                                "n_profil", "moving_avr", "gain_a0", "auto_gain_a0", "gain_a1", "auto_gain_a1", "R_Ny"]

        elif _data_format == "UDT003":
            self.data_type_c['bool_values'] = 'i'
            self.data_type_c['v_min_1'] = 'f'
            self.data_type_c['v_min_2'] = 'f'
            self.param_order = None
            self.param_order31 = ["bool_values", "tr_out", "f0", "prf", "R_Ny", "v_min_1", "v_min_2", "r_vol1",
                                  "r_dvol", "r_dsubvol", "n_vol", "n_subvol", "r_em", "n_ech", "n_profil", "moving_avr",
                                  "gain_a0", "gain_a1"]

            self.param_order32 = ["method", "v_min_1", "v_min_2", "tr_out", "tr_disposition", "f0", "prf", "r_vol1",
                                  "r_dvol", "r_dsubvol", "n_vol", "n_subvol", "r_em", "n_ech", "n_profil", "moving_avr",
                                  "gain_a0", "gain_a1", "R_Ny", "bool_values"]

        elif _data_format == "UDT004":
            self.data_type_c['bool_values'] = 'i'
            self.data_type_c['ref_config'] = 'i'
            self.data_type_c['v_min_1'] = 'f'
            self.data_type_c['v_min_2'] = 'f'
            self.param_order = ["bool_values", "ref_config", "tr_out", "f0", "prf", "R_Ny", "v_min_1", "v_min_2",
                                "r_vol1", "r_dvol", "r_dsubvol", "n_vol", "n_subvol", "r_em", "n_ech", "n_profil",
                                "moving_avr", "gain_a0", "gain_a1"]

        else:
            self.param_order = []
            # ~ "phase_coding", "d0", "d1", "d2", "n_profil", "moving_avr", "use_gain_function", "d3", "d4", "d5", "gain_a0", "gain_a1"]

    def extract_config(self, size, data):
        if self.param_order is None:
            select_data = unpack('iff', data[0: calcsize('iff')])[-1]
            if 2e5 < select_data and select_data < 2e7:  # check if frequency (200kHz / 20MHz)
                # select data
                self.param_order = self.param_order31
            else:
                self.param_order = self.param_order32

        elif len(self.param_order) == 8:
            head_size = calcsize('ifiiffffi')
            select_data = unpack('ifiiffffi', data[0: head_size])[-1]
            if select_data > 0 and select_data < 201:
                print("UDT001 old, select data, ", select_data)
                print(
                    "######### WARNING : check if phase_coding, static_echo_filter and d0 are OK !!! #####################")
                # select_data was most likely an integer, consider the old data format of UDT001
                # ~ self.param_order.extend(self.po_follow_11)
                self.param_order.extend(self.po_follow_2)
                # TODO1 mb 06/08/2021 : check à quoi correspond po_follow_1
                self.n_subvol.value = 1
            else:
                print("UDT001 update3, select data, ", select_data)
                # select_data was most likely a float, consider the newest data format of UDT001
                self.param_order.extend(self.po_follow_3)

        print(data)

        self.list_elem = {}
        head_size = 0
        for param in self.param_order:
            self.list_elem[param] = \
            unpack(self.data_type_c[param], data[head_size: head_size + calcsize(self.data_type_c[param])])[0]
            # unpack('%dh'%elem_size, data[head_size:head_size+size])
            head_size = head_size + calcsize(self.data_type_c[param])

            if param == "bool_values":
                print(self.list_elem[param])
                self.list_elem['auto_gain_a0'] = bool(self.list_elem[param] & 0x1)
                self.list_elem['auto_gain_a1'] = bool(self.list_elem[param] & 0x2)
                self.list_elem['phase_coding'] = bool(self.list_elem[param] & 0x4)
                self.list_elem['static_echo_filter'] = bool(self.list_elem[param] & 0x8)
                self.list_elem['IQ_tatency'] = bool(self.list_elem[param] & 0x10)
                if self.list_elem[param] & 0x20:
                    self.list_elem['V_em'] = 60
                else:
                    self.list_elem['V_em'] = 30
                self.list_elem['method'] = (self.list_elem[param] & 0x000F0000) >> 16
                self.list_elem['tr_disposition'] = (self.list_elem[param] & 0x00F00000) >> 20

        # Attention, il y a inversion entre le numéro associé à la bistatique et au transit selon les versions:
        if (size == 72 and self.data_format == "UDT001") or (self.data_format != "UDT004" and size == 76):
            if self.list_elem['tr_disposition'] == 1:
                self.list_elem['tr_disposition'] = 2
            elif self.list_elem['tr_disposition'] == 2:
                self.list_elem['tr_disposition'] = 1

        # sound speed extraction
        if "R_Ny" in self.list_elem:
            self.list_elem['sound_speed'] = self.list_elem["R_Ny"]*1.*self.list_elem["f0"] / self.list_elem["prf"]