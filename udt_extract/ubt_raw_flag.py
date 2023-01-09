# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

# Flags udt 4 and lower
ANS_TCP_CONFIG = 20000
ANS_TCP_PROFILE_INST = 20300
ANS_TCP_MEAS_TEMP = 20208  # la température
ANS_TCP_GAIN_AUTO = 20005  # les valeurs du gain

class Return_code_name():
    def __init__(self):

        self.reversed_code_dict = {10600: 'PING', 10700: 'DRIVER_VERSION', 10000: 'CONFIG', 10002: 'DATE',
                                   10400: 'START_RECORD',
                                   10500: 'STOP_RECORD', 10006: 'HALT', 10100: 'STOP', 10007: 'SET_TIMEOUT_SOCKET',
                                   10200: 'BLOC', 10201: 'STREAM',
                                   10203: 'STREAM_IQ', 10300: 'PROFILE_INST', 10303: 'PROFILE_DOPP',
                                   10302: 'PROFILE_MAVG', 10301: 'PROFILE_AAVG',
                                   10005: 'GAIN_AUTO', 10208: 'MEAS_TEMP', 10202: 'TEST_CONFIG', 10800: 'FRONT_ON',
                                   10900: 'FRONT_OFF', 11000: 'BATTERY',
                                   10010: 'OLD_GAIN_LOG'}

    def check(self, _code):
        if _code is None:
            return None
        elif _code >= 20000:
            _code -= 10000
        return self.reversed_code_dict.get(_code, None)