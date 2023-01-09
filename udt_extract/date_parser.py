# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

from dateutil.parser import parse


def date_parse(date_str):
	if str(date_str[0:4]).isdigit():
		# Ex : 2019-12-09
		return parse(date_str, yearfirst=True, dayfirst=False)
	else:
		# Ex : 09-12-2019
		return parse(date_str, dayfirst=True, yearfirst=False)
