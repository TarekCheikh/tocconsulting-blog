#! /usr/bin/env python
# coding:utf-8

"""oracle_export.py: This module is a generic python script used to help you
exporting Oracle databases using 'expdp' utility.
"""

__author__      = "Tarek OULD CHEIKH"
__license__     = "GPL"
__version__     = "1.0"
__maintainer__  = "Tarek OULD CHEIKH"
__email__       = "tarek@tocconsulting.fr"
__status__      = "Production"

import os
import subprocess
import sys

'''Setting database environment'''
def set_db_env(dbenv):
	# set up some environment variables
	dbenv["PATH"] = os.environ["PATH"]
	dbenv["ORACLE_HOME"] = os.getenv("ORACLE_HOME")
	dbenv["TNS_ADMIN"] = os.getenv("TNS_ADMIN")
	dbenv["LD_LIBRARY_PATH"] = os.getenv("LD_LIBRARY_PATH")

'''DB export'''
def db_export(dbenv):
	db_user = sys.argv[1]
	db_pass = sys.argv[2]
	db_alias = sys.argv[3]
	schema = sys.argv[4]
	dump_file = sys.argv[5]
	expdp_args = db_user + '/' + db_pass + '@' + db_alias + ' SCHEMAS=' + \
			schema + ' DUMPFILE=' + dump_file + \
			' DIRECTORY=DATA_PUMP_DIR'
	db_exp_work = subprocess.Popen(["expdp", expdp_args], \
				stdout=subprocess.PIPE, env=dbenv)
	if db_exp_work.wait() != 0:
		print "db_export() failed!"
		raise Exception("db_export() failed!")
	print "db_export() end!"

'''Printing help function'''
def help():
	print "Usage : %s db_user db_pass db_alias schema_to_export dump_file" \
		%(sys.argv[0])

if __name__=='__main__':
	if len(sys.argv) != 6:
		help()
		sys.exit(1)
	dbenv = {}
	set_db_env(dbenv)
	db_export(dbenv)
