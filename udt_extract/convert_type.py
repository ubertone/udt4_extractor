# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

import warnings
import json
import os

def warning_style(message, category, filename, lineno, file=None, line=None):
	return ' %s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)


warnings.formatwarning = warning_style

def clean_type(measure_type_string):
	"""
	This function allows us to clean the data type that we want to search.

	Only by lowering the input, and replacing every '-' by '_'.

	Parameters
	----------
	measure_type_string: str
		The input, what we want to clean.

	Returns
	-------
	res: str
		What we just cleaned.
	"""
	lower = measure_type_string.lower()
	res = lower.replace("-", "_")

	# remove all white spaces and beginning or end of the string
	tocheck = 1
	while tocheck:
		if res[0]!=" " and res[-1]!=" ":
			tocheck=0
		elif res[0]==" ":
			res = res[1:]
		elif res[-1]==" ":
			res = res[:-1]

	# replace white spaces in the middle of the string by underscores
	return res.replace(" ","_")

def translate_key(raw_key, _type="data"):
	"""
	Translate data_types through a translation json file. Returns None if raw_key not in json file.

	Parameters
	----------
	raw_key: string

	Returns
	-------
	translated_key: string or None
	"""

	translated_key = None

	# use of a json file for the translation in valid data type names for the DB
	_transation_path =  os.path.dirname(os.path.realpath(__file__))+'/translation.json'
	f = open(_transation_path)
	translation_dict = json.loads(f.read())[_type]

	for key, value in translation_dict.items():
		# leave unchanged the already valid data type names
		# translate those which are translatable
		if (raw_key == key):
			translated_key = key
			break
		elif value["alter_ego"] is not None:
			if raw_key in value["alter_ego"]:
				translated_key = key
				break

	#if translated_key == None:
	#	print("delete %s"%raw_key)
	return translated_key

def translate_paramdict(param_dict):
	"""
	Parse a dict and translate param_names and clean out those not to be imported in the ORM

	Parameters
	----------
	param_dicts: dict

	Returns
	-------
	param_dict: dict
	"""
	translated_param_dict = {}
	for key,elem in param_dict.items():
		if translate_key(clean_type(key),_type="param_var") is not None:
			translated_param_dict[translate_key(clean_type(key),_type="param_var")] = elem
		elif translate_key(clean_type(key),_type="param_const") is not None:
			translated_param_dict[translate_key(clean_type(key), _type="param_const")] = elem
	return translated_param_dict

def translate_datadictslist(data_dicts):
	"""
	Parse a list of dicts and translate data_types and clean out those not to be imported in the ORM
	Can be used on scalar or vector dicts.

	Parameters
	----------
	data_dicts: list(dict)

	Returns
	-------
	importable_data_dicts: list(dict)
	"""
	importable_data_dicts = []
	i=0
	for data_dict in data_dicts:
		importable_data_dicts.append(data_dict)
		# standardisation of the data type names --> only underscores and lower case
		importable_data_dicts[i]['name'] = clean_type(data_dict['name'])

		# traduire les noms qui ont une traduction (cf switcher dans convert_type.py)
		importable_data_dicts[i]['name'] = translate_key(importable_data_dicts[i]['name'], _type="data")
		if importable_data_dicts[i]['name'] is None:
		# supprimer les lignes sont le type n'existe pas la la liste de données importables
			del importable_data_dicts[i]
		else:
			i=i+1

	return importable_data_dicts
