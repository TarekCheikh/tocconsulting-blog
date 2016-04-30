#! /usr/bin/env python
# coding:utf-8

"""download_from_rds.py: This module is a generic python script used to help you
downloading Oracle DUMP files from an Oracle RDS instance.
This module use download_from_rds.conf as config file.
"""

__author__      = "Tarek OULD CHEIKH"
__license__     = "GPL"
__version__     = "1.0"
__maintainer__  = "Tarek OULD CHEIKH"
__email__       = "tarek@tocconsulting.fr"
__status__      = "Production"

import cx_Oracle
import sys 
import ConfigParser
import os.path

# Configuration file
CONF_FILE = os.path.basename(__file__).split('.')[0] + '.conf'
# The list containing conf values
CONF_VALUES = {}
# Remote directory inside RDS
DB_DUMPS_DIR = "DATA_PUMP_DIR"
# Transfert data using this chunk size
DATA_CHUNK = 32767

'''Read and parse configuration file'''
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
		CONF_VALUES['DEST_DIR'] = parser.get('DUMP Files', \
			'DEST_DIR')
	except IOError as e:
		print "I/O error : %s" %e
		sys.exit(1)

'''Connect to the Oracle database'''
def db_connection():
	# Open db connection
	connection = cx_Oracle.connect(CONF_VALUES['RDS_USER'], \
		CONF_VALUES['RDS_PASS'], CONF_VALUES['RDS_SID'])

	return connection

'''Donwload the remote dump'''
def download_db_dumps(connection):
	# Create our cusror
	cursor = connection.cursor()
	for dump_file in CONF_VALUES['DUMP_FILES'].split(","):
		sql_get_dump = "SELECT BFILENAME('DATA_PUMP_DIR','" \
				+ dump_file + "') FROM dual"
		try:
			cursor.execute(sql_get_dump)
			for remote_dump in cursor:
				dump_size_bytes = remote_dump[0].size()
				print "Dump size in KB ==> %s" \
					%(int(dump_size_bytes)/1024.)
				# Wrting the dump on our local machine
				with open(CONF_VALUES['DEST_DIR'] + '/' + \
					dump_file, 'w+') as f:
					read_size = 0
					while read_size < int(dump_size_bytes):
						dump_data = \
							remote_dump[0].read(\
								read_size + 1, \
								DATA_CHUNK)
						read_size += len(dump_data)
						f.write(dump_data)
		except cx_Oracle.DatabaseError, exc:
			error, = exc.args
			print "Oracle-Error-Code: %s" %error.code
			print "Oracle-Error-Message: %s" %error.message
	# Closing cursor
        cursor.close()

# Script entry point
if __name__ =="__main__":
	get_conf(CONF_FILE)
	# Connecting to the database
	connection = db_connection()
	# Perform download
	download_db_dumps(connection)
	# Close connection
	connection.close()
