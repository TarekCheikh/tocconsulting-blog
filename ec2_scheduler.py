#! /usr/bin/env python
# coding:utf-8

"""ec2_scheduler.py: This module is a generic python script used to start/stop
AWS ec2 instances based on tags.
This module use ec2_scheduler.conf as configuration file.
"""

__author__ 	= "Tarek OULD CHEIKH"
__copyright__ 	= "Copyright 2016, TOC CONSULTING"
__license__ 	= "GPL"
__version__ 	= "0.1"
__maintainer__ 	= "Tarek OULD CHEIKH"
__email__ 	= "tarek@tocconsulting.fr"
__status__ 	= "Production"

import sys
import os.path
import time
import logging
import ConfigParser
import boto3
import datetime

# Log filename
LOG_FILE = os.path.basename(__file__).split('.')[0] + \
	time.strftime("_%Y%m%d-%H%M%S") + '.log'
# Configuration file
CONF_FILE = os.path.basename(__file__).split('.')[0] + '.conf'
# The list containing conf values
CONF_VALUES = {}
# List of instances to start/stop
start_list = []
stop_list = []

'''Init log file.'''
def init_log_file(log_file):
	# Set log file name and format
	logging.basicConfig(filename=log_file, level=logging.INFO,\
		format='%(asctime)s - %(funcName)s - %(levelname)s - \
			%(message)s', datefmt='')

'''Read and parse configuration file.'''
def get_conf(conf_file):
	logging.info('Reading configuration file')
	try:
		parser = ConfigParser.ConfigParser()
		parser.read(CONF_FILE)
		CONF_VALUES['AWS_PROFILE'] = parser.get('AWS Credentials', \
			'AWS_PROFILE')
		CONF_VALUES['SCHEDULE_TAG'] = parser.get('EC2 instances', \
			'SCHEDULE_TAG')
	except IOError as e:
		logging.error('I/O error : %s' % e)
		sys.exit(1)

'''Logging all infos from conf file'''
def dump_conf():
        logging.info('Getting this config :')
        logging.info('AWS pofile ==> %s' % CONF_VALUES['AWS_PROFILE'])
        logging.info('Schedule tag ==> %s' % CONF_VALUES['SCHEDULE_TAG'])

'''Connect to aws and get an "ec2" resource'''
def init_session():
	logging.info('Begin init_session')
	session = boto3.session.Session(profile_name=CONF_VALUES['AWS_PROFILE'])
	#ec2_resource = session.resource('ec2')
	logging.info('End init_session')
	#return ec2_resource
	return session

'''Getting id from an ec2 instance object'''
def get_instance_tag(instance, tag):
	logging.info('Begin get_instance_tag')
	if instance.tags is None:
		logging.info('End get_instance_tag')
		return None
	for t in instance.tags:
		if t['Key'] == tag:
			logging.info('End get_instance_tag')
			return t['Value']

	logging.info('End get_instance_tag')
	return None

'''Getting ec2 instance name if exist'''
def get_instance_name(instance):
	logging.info('Begin get_instance_name')
	if instance.tags is None:
		logging.info('End get_instance_name')
		return None
	for t in instance.tags:
		if t['Key'] == 'Name':
			logging.info('End get_instance_name')
			return t['Value']
	
	logging.info('End get_instance_name')
	return None

'''Getting ec2 instance state'''
def get_instance_state(instance):
	return (instance.state)['Name']

'''Check if instance is running'''
def is_instance_running(instance):
	return (get_instance_state(instance) == 'running')

'''Check if instance is stopped'''
def is_instance_stopped(instance):
	return (get_instance_state(instance) == 'stopped')

'''Getting ec2 start/stop hours from the tag "CONF_VALUES['SCHEDULE_TAG']"'''
def get_schedule_hours(tag):
	return (tag.split('-')[0], tag.split('-')[1])

'''Determine which action to to do, start or stop on the ec2 instance
and add it to the right action list
'''
def enqueue_schedule_action(now_hour, stop_hour, start_hour, \
		instance_state, instance_id):
	logging.info('Begin enqueue_schedule_action')
	stop = (int)(stop_hour)
	start = (int)(start_hour)
	if start == 0:
		start = 24
	if stop == 0:
		stop = 24
	# TODO : Handle when the user stop instances
	if (instance_state == 'running'):
		if ((now_hour >= start) and (now_hour < stop)):
			# We do nothing in this case
			pass
		else:
			# Add to stop list
			stop_list.append(instance_id)
	elif (instance_state == 'stopped'):
		if ((now_hour >= start) and (now_hour < stop)):	
			# Add to start list
			start_list.append(instance_id)
		else:
			pass
	else:
		pass
	logging.info('End enqueue_schedule_action')

'''Perform stop/start actions'''
def dequeue_schedule_action(client):
	logging.info('Begin dequeue_schedule_action')
	# Stop instances
	logging.info('Stopping instances ==> %s' %stop_list)	
	if stop_list:
		client.stop_instances(InstanceIds=stop_list)
	# Start instances	
	logging.info('Starting instances ==> %s' %start_list)
	if start_list:
		client.start_instances(InstanceIds=start_list)
	logging.info('End dequeue_schedule_action')

# Script entry point
# Redirect STDOUT to /dev/null
stdout_file = open('/dev/null', 'w')
sys.stdout = stdout_file
# Redirect STDERR to /dev/null
sys.stderr = stdout_file

try:
	now = datetime.datetime.now()
	init_log_file(LOG_FILE)
	logging.info('AWS ec2 scheduler Start and now = %s' %now)
	get_conf(CONF_FILE)
	dump_conf()
	session = init_session()
	# Getting an 'ec2' resource
	ec2 = session.resource('ec2')
	instances = ec2.instances.all()
	for instance in instances:
		schedule_tag_value = get_instance_tag(instance, \
			CONF_VALUES['SCHEDULE_TAG'])
		if schedule_tag_value:
			logging.info('Instance ID ==> %s and Name ==>' \
				'%s and tag %s' % (instance.id, \
				get_instance_name(instance), \
                                schedule_tag_value))
			start_time, stop_time = \
				get_schedule_hours(schedule_tag_value)
			logging.info('Instance start and stop hours' \
					'==> %s/%s' %(start_time, stop_time))
			instance_state = get_instance_state(instance)
			logging.info('Instance state ==> %s' % instance_state)
			now_hour = (int)(now.hour)
			enqueue_schedule_action(now_hour, stop_time, \
					start_time, instance_state, instance.id)
	# We need an ec2 client
	ec2_client = session.client('ec2')
	dequeue_schedule_action(ec2_client)

except Exception as e:
	# Log the exception
	logging.info('Got this error %s' % e)
