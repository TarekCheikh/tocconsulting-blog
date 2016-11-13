#! /usr/bin/env python
# coding:utf-8

"""gen_webapp_aws.py: This module is used to generate
the WEBAPP project Aws infra and app.
This module use gen_webapp_aws.conf as configuration file.
"""

__author__      = "Tarek OULD CHEIKH"
__copyright__   = "Copyright 2016, TOC CONSULTING"
__license__     = "GPL"
__version__     = "0.1"
__maintainer__  = "Tarek OULD CHEIKH"
__email__       = "tarek@tocconsulting.fr"
__status__      = "Production"

import sys
import os
import time
import logging
import ConfigParser
import boto3
import re
import shutil
from termcolor import colored, cprint
import botocore
 
# Log filename
LOG_FILE = os.path.basename(__file__).split('.')[0] + \
        time.strftime("_%Y%m%d-%H%M%S") + '.log'
# Configuration file
CONF_FILE = os.path.basename(__file__).split('.')[0] + '.conf'
# The list containing conf values
CONF_VALUES = {}
# all statuses except (DELETE_COMPLETE)
RUNNING_STATUSES = [
	'CREATE_IN_PROGRESS',
	'CREATE_FAILED',
	'CREATE_COMPLETE',
	'ROLLBACK_IN_PROGRESS',
	'ROLLBACK_FAILED',
	'ROLLBACK_COMPLETE',
	'DELETE_IN_PROGRESS',
	'DELETE_FAILED',
	'UPDATE_IN_PROGRESS',
	'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
	'UPDATE_COMPLETE',
	'UPDATE_ROLLBACK_IN_PROGRESS',
	'UPDATE_ROLLBACK_FAILED',
	'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
	'UPDATE_ROLLBACK_COMPLETE'
]

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
		CONF_VALUES['AWS_ACCOUNT_ID'] = parser.get('AWS Credentials', \
			'AWS_ACCOUNT_ID')
		CONF_VALUES['ENV_TAG'] = parser.get('WEBAPP Env', \
			'ENV_TAG')
		CONF_VALUES['INFRA_KEYPAIR'] = parser.get('WEBAPP Infra', \
			'INFRA_KEYPAIR')
		CONF_VALUES['BASTION_AMI'] = parser.get('WEBAPP Infra', \
			'BASTION_AMI')
		CONF_VALUES['BASTION_INST_TYPE'] = parser.get('WEBAPP Infra', \
			'BASTION_INST_TYPE')
		CONF_VALUES['NAT_AMI'] = parser.get('WEBAPP Infra', \
			'NAT_AMI')
		CONF_VALUES['NAT_INST_TYPE'] = parser.get('WEBAPP Infra', \
			'NAT_INST_TYPE')
		CONF_VALUES['APP_KEYPAIR'] = parser.get('WEBAPP App', \
			'APP_KEYPAIR')
		CONF_VALUES['PG_AMI'] = parser.get('WEBAPP App', \
			'PG_AMI')
		CONF_VALUES['PG_INST_TYPE'] = parser.get('WEBAPP App', \
			'PG_INST_TYPE')
		CONF_VALUES['BACK_AMI'] = parser.get('WEBAPP App', \
			'BACK_AMI')
		CONF_VALUES['BACK_INST_TYPE'] = parser.get('WEBAPP App', \
			'BACK_INST_TYPE')
		CONF_VALUES['CF_TEMPLATE_FILE'] = parser.get( \
			'Cloudformation Template', 'CF_TEMPLATE_FILE')
		CONF_VALUES['CF_UPDATE_POLICY_FILE'] = parser.get( \
			'Cloudformation Template', 'CF_UPDATE_POLICY_FILE')
		CONF_VALUES['CF_STACK_NAME'] = parser.get( \
			'Cloudformation Template', 'CF_STACK_NAME')
		CONF_VALUES['CF_TEMPLATE_S3_BUCKET'] = parser.get( \
			'Cloudformation Template', 'CF_TEMPLATE_S3_BUCKET')
	except IOError as e:
		logging.error('I/O error : %s' % e)
		sys.exit(1)

'''Logging all infos from conf file'''
def dump_conf():
	logging.info('Getting this config :')
	logging.info('AWS pofile ==> %s' % CONF_VALUES['AWS_PROFILE'])
	logging.info('AWS account id ==> %s' % CONF_VALUES['AWS_ACCOUNT_ID'])
	logging.info('Webapp env ==> %s' % CONF_VALUES['ENV_TAG'])
	logging.info('Infra keypair ==> %s' % CONF_VALUES['INFRA_KEYPAIR'])
	logging.info('Bastion ami ==> %s' % CONF_VALUES['BASTION_AMI'])
	logging.info('Bastion inst type ==> %s' \
		% CONF_VALUES['BASTION_INST_TYPE'])
	logging.info('Nat ami ==> %s' % CONF_VALUES['NAT_AMI'])
	logging.info('Nat inst type ==> %s' % CONF_VALUES['NAT_INST_TYPE'])
	logging.info('App keypair ==> %s' % CONF_VALUES['APP_KEYPAIR'])
	logging.info('Pg ami ==> %s' % CONF_VALUES['PG_AMI'])
	logging.info('Pg inst type ==> %s' % CONF_VALUES['PG_INST_TYPE'])
	logging.info('Back ami ==> %s' % CONF_VALUES['BACK_AMI'])
	logging.info('Back inst type ==> %s' % CONF_VALUES['BACK_INST_TYPE'])
	logging.info('Cloudformation template file ==> %s' \
		% CONF_VALUES['CF_TEMPLATE_FILE'])
	logging.info('Cloudformation policy file ==> %s' \
		% CONF_VALUES['CF_UPDATE_POLICY_FILE'])
	logging.info('Cloudformation stack name ==> %s' \
		% CONF_VALUES['CF_STACK_NAME'])
	logging.info('S3 bucket for templates ==> %s' \
		% CONF_VALUES['CF_TEMPLATE_S3_BUCKET'])

'''Init AWS session'''
def init_session():
	logging.info('Begin init_session')
	session = boto3.session.Session(profile_name=CONF_VALUES['AWS_PROFILE'])
	logging.info('End init_session')

	return session

'''Replacing all occurences of a string inside a file'''
def replace_text(file_name, pattern, new_text):
	with open(file_name, "r") as text:
		lines = text.readlines()
	with open(file_name, "w") as text:
		for line in lines:
			text.write(re.sub(pattern, new_text, line))

'''Check if the stack exists'''
def stack_exists(cfn_client, stack_name):
	stacks_desc = cfn_client.list_stacks(StackStatusFilter=RUNNING_STATUSES)
	stacks_list = stacks_desc['StackSummaries']
	# Handle empty list of stacks
	if len(stacks_list) == 0:
		return False
	for stack in stacks_list:
		if stack['StackName'] == stack_name:
			return True

	return False

'''Check Template'''
def validate_template(cfn_client, template_url):
	# Validate cf json template file
        response = cfn_client.validate_template(TemplateURL=template_url)
	logging.info('Got this response on validation ==> %s' % response)

'''Log the given event'''
def print_event_log(log_event_dict):
	date_log = colored(time.strftime("%Y-%m-%d %H:%M:%S"), 'white')
	resource_name = log_event_dict['resource_name']
	resource_name_log = colored('%50s\t\t==>' %resource_name, 'white')
	resource_status = log_event_dict['resource_status']
	resource_status_color = log_event_dict['resource_status_color']
	resource_status_log = colored('%s' %resource_status, \
		resource_status_color, attrs=['bold'])
	print date_log, resource_name_log, resource_status_log
	sys.stdout.flush()

'''Waiting for the stack to complete CREATE/UPDATE'''
def wait_for_stack_to_complete(cfn_client):
	is_complete = False
	resources_in_progress = set()
	resources_complete = set()

	while not is_complete:
		time.sleep(20)
		event_list = (cfn_client.describe_stack_events(\
			StackName=CONF_VALUES['CF_STACK_NAME']))['StackEvents']

		# Get Reverse chronological order
		event_list.reverse()
		for event in event_list:
			resource_name = event['LogicalResourceId']
			resource_status = event['ResourceStatus']
			if resource_status == 'CREATE_IN_PROGRESS':
				if resource_name not in resources_in_progress:
					log_event_dict = {}
					log_event_dict['resource_name'] = \
						resource_name
					log_event_dict['resource_status'] = \
						'CREATE_IN_PROGRESS'
					log_event_dict['resource_status_color']\
						= 'yellow'
					print_event_log(log_event_dict)
					log_event_dict.clear()
					resources_in_progress.add(resource_name)
					#time.sleep(1)
			else:
				if resource_name == \
					CONF_VALUES['CF_STACK_NAME']:
					is_complete = True
				else:
					if resource_name not in \
						resources_complete:
						log_event_dict = {}
						log_event_dict['resource_name']\
							= resource_name
						log_event_dict[\
							'resource_status'] = \
							'CREATE_COMPLETE'
						log_event_dict[\
							'resource_status_color'\
							] = 'green'
						print_event_log(log_event_dict)
						log_event_dict.clear()
						resources_complete.add(\
							resource_name)
	
	log_event_dict = {}
	log_event_dict['resource_name'] = CONF_VALUES['CF_STACK_NAME']
	log_event_dict['resource_status'] = 'CREATE_COMPLETE'
	log_event_dict['resource_status_color'] = 'green'
	print_event_log(log_event_dict)
	log_event_dict.clear()

'''Create cloudformation stack'''
def create_or_update_cfn_stack(cfn_client, 
				template_cfn_url, template_policy_url):
	if (stack_exists(cfn_client, CONF_VALUES['CF_STACK_NAME'])):
		logging.info('Stack already exist! Update it')
		try :
			response = cfn_client.update_stack(
				StackName=CONF_VALUES['CF_STACK_NAME'],
				TemplateURL=template_url,
				StackPolicyDuringUpdateURL=template_policy_url,
				Capabilities=[
					'CAPABILITY_IAM',
				],
			)
		except botocore.exceptions.ClientError as e:
			if (e.response['Error']['Message'] == \
				'No updates are to be performed.'):
				print 'No update to perform'
				raise Exception('No update to perform BYE')
			else:
				raise
	else:
		response = cfn_client.create_stack(
			StackName=CONF_VALUES['CF_STACK_NAME'],
			TemplateURL=template_url,
			TimeoutInMinutes=20,
			Capabilities=[
				'CAPABILITY_IAM',
			],
			OnFailure='ROLLBACK',
			Tags=[
				{
					'Key': 'Name',
					'Value': CONF_VALUES['CF_STACK_NAME']
				},
			]
		)
		logging.info('Got this response on creation ==> %s' % response)

'''Check if file exist inside bucket'''
def s3_file_exists(s3_client, bucket_name, s3_file):
	response = s3_client.list_objects(Bucket=bucket_name)
	s3_files = response['Contents']

	for file in s3_files:
		filename = file['Key']
		if filename == s3_file:
			return True
	
	return False

'''Check if a bucket exist'''
def bucket_exists(s3_client, bucket_name):
	try:
		s3_client.head_bucket(Bucket=bucket_name)
		
		return True
	except:
		logging.info('Bucket %s does not exist' % bucket_name)
	
		return False

'''Create S3 templates bucket'''
def create_s3_templates_bucket(s3_client, bucket_name):
	response = s3_client.create_bucket(Bucket=bucket_name,
				CreateBucketConfiguration=\
					{'LocationConstraint': 'eu-west-1'})

	logging.info('Got this response on bucket creation ==> %s' % response)

'''Upload the template to S3 bucket'''
def upload_file_to_s3(s3_client, bucket_name, cfn_file):
	remote_cfn_file = (cfn_file.split('/'))[-1]
	response = s3_client.upload_file(cfn_file, bucket_name, remote_cfn_file)

	logging.info('Got this response on template upload ==> %s' % response)

# Script entry point
if __name__ == '__main__':
	try:
		init_log_file(LOG_FILE)
		logging.info('Aws Webapp Infra and App deploy begin')
		get_conf(CONF_FILE)
		dump_conf()
		# Create cloudformation json file from template
		cfn_file = os.path.dirname(os.path.realpath(__file__)) + \
			'/webapp-cfn-' + CONF_VALUES['ENV_TAG'] + \
			time.strftime("_%Y%m%d-%H%M%S") + '.json'
		shutil.copyfile(CONF_VALUES['CF_TEMPLATE_FILE'], cfn_file)
		for param in CONF_VALUES:
			replace_text(cfn_file, param, CONF_VALUES[param])
        	session = init_session()
		# Create S3 templates bucket if nexessary
		# Getting an S3 client
		s3_client = session.client('s3')
		bucket_name = CONF_VALUES['CF_TEMPLATE_S3_BUCKET']
		if not bucket_exists(s3_client, bucket_name):
			create_s3_templates_bucket(s3_client, bucket_name)
		# Upload template file to S3 bucket
		upload_file_to_s3(s3_client, bucket_name, cfn_file)
		# Upload policy template file if necessary
		policy_file_path = CONF_VALUES['CF_UPDATE_POLICY_FILE']
		policy_file = (policy_file_path.split('/'))[-1]
		if not s3_file_exists(s3_client, bucket_name, policy_file):
			upload_file_to_s3(s3_client, bucket_name, \
				policy_file_path)
		# Getting a 'cloudformation' client
		cfn_client = session.client('cloudformation')
		# Validate cf template
		template_url = "http://" + bucket_name + \
			".s3.amazonaws.com/" + (cfn_file.split('/'))[-1]
		validate_template(cfn_client, template_url)

		template_policy_url = "http://" + bucket_name + \
			".s3.amazonaws.com/" + policy_file
		# Create or Update the stack
		create_or_update_cfn_stack(cfn_client, template_url, \
				template_policy_url)
		wait_for_stack_to_complete(cfn_client)

	except Exception as e:
		# Log the exception
		logging.info('Got this error %s' % e)

