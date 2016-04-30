#! /usr/bin/env python
# coding:utf-8

"""upload_to_rds.py: This module is a generic python script used to help you
uploading Oracle DUMP files to an Oracle RDS instance.
This module use upload_to_rds.conf as config file.
"""

__author__      = "Tarek OULD CHEIKH"
__license__     = "GPL"
__version__     = "1.0"
__maintainer__  = "Tarek OULD CHEIKH"
__email__       = "tarek@tocconsulting.fr"
__status__      = "Production"

import cx_Oracle
import sys 
import logging
import ConfigParser
import os.path

# Configuration file
CONF_FILE = os.path.basename(__file__).split('.')[0] + '.conf'
# The list containing conf values
CONF_VALUES = {}
# Remote directory inside RDS
DEST_DIR_NAME = "DATA_PUMP_DIR"
# Transfert data using this chunk size
DATA_CHUNK = 32767

'''Read and parse configuration file.'''
def get_conf(conf_file):
	try:
		parser = ConfigParser.ConfigParser()
		parser.read(CONF_FILE)
		CONF_VALUES['RDS_PORT'] = parser.get('RDS Infos', \
			'RDS_PORT')
		CONF_VALUES['RDS_HOST'] = parser.get('RDS Infos', \
			'RDS_HOST')
		CONF_VALUES['RDS_USER'] = parser.get('RDS Infos', \
			'RDS_USER')
		CONF_VALUES['RDS_PASS'] = parser.get('RDS Infos', \
			'RDS_PASS')
		CONF_VALUES['RDS_SID'] = parser.get('RDS Infos', \
			'RDS_SID')
		CONF_VALUES['DUMP_FILES'] = parser.get('DUMP Files', \
			'DUMP_FILES')
	except IOError as e:
		logging.error('I/O error : %s' % e)
		sys.exit(1)

# Script entry point
get_conf(CONF_FILE)

sql_dump_file_open = "BEGIN RDS_UPLOAD_PACKAGE.FH := UTL_FILE.FOPEN(" + \
			":DIRNAME, :FNAME, 'WB', :CHUNK); END;";
sql_dump_file_write = "BEGIN UTL_FILE.PUT_RAW(RDS_UPLOAD_PACKAGE.FH, :DATA," + \
			" TRUE); END;";
sql_dump_file_close = "BEGIN UTL_FILE.FCLOSE(RDS_UPLOAD_PACKAGE.FH); END;";
sql_create_package = "CREATE OR REPLACE PACKAGE RDS_UPLOAD_PACKAGE " + \
			"AS FH UTL_FILE.FILE_TYPE; END;";

# DB coonection string
RDS_DB_STRING = CONF_VALUES['RDS_HOST'] + ":" + CONF_VALUES['RDS_PORT'] + \
		"/" + CONF_VALUES['RDS_SID']

# Open connection
connection = cx_Oracle.connect(CONF_VALUES['RDS_USER'], \
		CONF_VALUES['RDS_PASS'], RDS_DB_STRING)
# Create our cusror
cursor = connection.cursor()
cursor.execute(sql_create_package)
for dump_file in CONF_VALUES['DUMP_FILES'].split(","):
	cursor.execute(sql_dump_file_open, dirname=DEST_DIR_NAME, \
			fname=dump_file, chunk=DATA_CHUNK)

	local_dump_file = open(dump_file, 'rb')
	while True:
		data = local_dump_file.read(DATA_CHUNK)
		if not data:
			break
		# We are uploading binary data
		binary_var = cursor.var(cx_Oracle.BLOB)
		binary_var.setvalue(0, data) 
		cursor.execute(sql_dump_file_write, data=binary_var)

	# Closing uploaded dump file
	cursor.execute(sql_dump_file_close)
	# Close local file
	local_dump_file.close()
