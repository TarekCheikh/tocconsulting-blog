#! /usr/bin/env python
# coding:utf-8

"""create_aws_ec2.py: This module is used to generate
an aws ec2 instance.
This module use create_aws_ec2.conf as configuration file.
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

'''Init log file.'''
def init_log_file(log_file):
	# Set log file name and format
	logging.basicConfig(filename=log_file, level=logging.INFO,\
		format='%(asctime)s - %(funcName)s:%(lineno)s - %(levelname)s' \
			' - %(message)s', datefmt='')

'''Read and parse configuration file.'''
def get_conf(conf_file):
	logging.info('Reading configuration file')
	print_event_log('Reading configuration file')

	try:
		parser = ConfigParser.ConfigParser()
		parser.read(CONF_FILE)
		CONF_VALUES['AWS_PROFILE'] = parser.get('AWS Credentials', \
			'AWS_PROFILE')
		CONF_VALUES['AWS_ACCOUNT_ID'] = parser.get('AWS Credentials', \
			'AWS_ACCOUNT_ID')
		CONF_VALUES['NAME_TAG'] = parser.get('EC2 Infos', \
			'NAME_TAG')
		CONF_VALUES['ENV_TAG'] = parser.get('EC2 Infos', \
			'ENV_TAG')
		CONF_VALUES['EC2_KEYPAIR'] = parser.get('EC2 Infos', \
			'EC2_KEYPAIR')
		CONF_VALUES['EC2_AMI'] = parser.get('EC2 Infos', \
			'EC2_AMI')
		CONF_VALUES['EC2_INST_TYPE'] = parser.get('EC2 Infos', \
			'EC2_INST_TYPE')
		CONF_VALUES['EC2_VPC_ID'] = parser.get('EC2 Infos', \
			'EC2_VPC_ID')
		CONF_VALUES['EC2_SUBNET_ID'] = parser.get( \
			'EC2 Infos', 'EC2_SUBNET_ID')
		CONF_VALUES['EC2_AZ'] = parser.get( \
			'EC2 Infos', 'EC2_AZ')
		CONF_VALUES['EC2_IAM_ROLE'] = parser.get( \
			'EC2 Infos', 'EC2_IAM_ROLE')
		CONF_VALUES['EC2_VOLUME_SIZE'] = parser.get( \
			'EC2 Infos', 'EC2_VOLUME_SIZE')
		CONF_VALUES['EC2_VOLUME_TYPE'] = parser.get( \
			'EC2 Infos', 'EC2_VOLUME_TYPE')
		CONF_VALUES['EC2_USER_DATA'] = parser.get( \
			'EC2 Infos', 'EC2_USER_DATA')
		CONF_VALUES['EC2_PRIV_IP'] = parser.get( \
			'EC2 Infos', 'EC2_PRIV_IP')
		CONF_VALUES['EC2_HAS_PUB_IP'] = parser.get( \
			'EC2 Infos', 'EC2_HAS_PUB_IP')
		CONF_VALUES['EC2_SG_RULES'] = parser.get( \
			'EC2 Infos', 'EC2_SG_RULES')
		CONF_VALUES['EC2_SG_NAME'] = parser.get( \
			'EC2 Infos', 'EC2_SG_NAME')
		CONF_VALUES['EC2_SG_DESC'] = parser.get( \
			'EC2 Infos', 'EC2_SG_DESC')
	except IOError as e:
		logging.error('I/O error : %s' % e)
		print_event_log('I/O error : %s' % e)
		sys.exit(1)

'''Logging all infos from conf file'''
def dump_conf():
	logging.info('Getting this config :')
	print_event_log('Getting this config :')
	logging.info('AWS pofile ==> %s' % CONF_VALUES['AWS_PROFILE'])
	print_event_log('AWS pofile ==> %s' % CONF_VALUES['AWS_PROFILE'])
	logging.info('AWS account id ==> %s' % CONF_VALUES['AWS_ACCOUNT_ID'])
	print_event_log('AWS account id ==> %s' % CONF_VALUES['AWS_ACCOUNT_ID'])
	logging.info('EC2 Name Tag ==> %s' % CONF_VALUES['NAME_TAG'])
	print_event_log('EC2 Name Tag ==> %s' % CONF_VALUES['NAME_TAG'])
	logging.info('EC2 Env Tag ==> %s' % CONF_VALUES['ENV_TAG'])
	print_event_log('EC2 Env Tag ==> %s' % CONF_VALUES['ENV_TAG'])
	logging.info('EC2 keypair ==> %s' % CONF_VALUES['EC2_KEYPAIR'])
	print_event_log('EC2 keypair ==> %s' % CONF_VALUES['EC2_KEYPAIR'])
	logging.info('EC2 ami ==> %s' % CONF_VALUES['EC2_AMI'])
	print_event_log('EC2 ami ==> %s' % CONF_VALUES['EC2_AMI'])
	logging.info('EC2 inst type ==> %s' % CONF_VALUES['EC2_INST_TYPE'])
	print_event_log('EC2 inst type ==> %s' % CONF_VALUES['EC2_INST_TYPE'])
	logging.info('EC2 vpc id ==> %s' % CONF_VALUES['EC2_VPC_ID'])
	print_event_log('EC2 vpc id ==> %s' % CONF_VALUES['EC2_VPC_ID'])
	logging.info('EC2 subnet id ==> %s' % CONF_VALUES['EC2_SUBNET_ID'])
	print_event_log('EC2 subnet id ==> %s' % CONF_VALUES['EC2_SUBNET_ID'])
	logging.info('EC2 Availability Zone ==> %s' % CONF_VALUES['EC2_AZ'])
	print_event_log('EC2 Availability Zone ==> %s' % CONF_VALUES['EC2_AZ'])
	logging.info('EC2 IAM Role ==> %s' % CONF_VALUES['EC2_IAM_ROLE'])
	print_event_log('EC2 IAM Role ==> %s' % CONF_VALUES['EC2_IAM_ROLE'])
	logging.info('EC2 Volume Size ==> %s' % CONF_VALUES['EC2_VOLUME_SIZE'])
	print_event_log('EC2 Volume Size ==> %s' \
			% CONF_VALUES['EC2_VOLUME_SIZE'])
	logging.info('EC2 Volume Type ==> %s' % CONF_VALUES['EC2_VOLUME_TYPE'])
	print_event_log('EC2 Volume Type ==> %s' \
			% CONF_VALUES['EC2_VOLUME_TYPE'])
	logging.info('EC2 UserData ==> %s' % CONF_VALUES['EC2_USER_DATA'])
	print_event_log('EC2 UserData ==> %s' % CONF_VALUES['EC2_USER_DATA'])
	logging.info('EC2 Private Ip ==> %s' % CONF_VALUES['EC2_PRIV_IP'])
	print_event_log('EC2 Private Ip ==> %s' % CONF_VALUES['EC2_PRIV_IP'])
	logging.info('EC2 Has Public Ip ==> %s' % CONF_VALUES['EC2_HAS_PUB_IP'])
	print_event_log('EC2 Has Public Ip ==> %s' \
			% CONF_VALUES['EC2_HAS_PUB_IP'])
	logging.info('EC2 SG Name ==> %s' % CONF_VALUES['EC2_SG_NAME'])
	print_event_log('EC2 SG Name ==> %s' % CONF_VALUES['EC2_SG_NAME'])
	logging.info('EC2 SG Desc ==> %s' % CONF_VALUES['EC2_SG_DESC'])
	print_event_log('EC2 SG Desc ==> %s' % CONF_VALUES['EC2_SG_DESC'])
	sg_rules = CONF_VALUES['EC2_SG_RULES'].split(',')
	for sg in sg_rules:
		logging.info('EC2 Has Rule ==> %s' % sg)
		print_event_log('EC2 Has Rule ==> %s' % sg)

'''Log the given event'''
def print_event_log(event_log):
	date_log = colored(time.strftime("%Y-%m-%d %H:%M:%S"), 'white')
	event_log_with_color = colored('%s' %event_log, 'green')
	print date_log, event_log_with_color
	sys.stdout.flush()

'''Init AWS session'''
def init_session():
	logging.info('Begin init_session')
	print_event_log('Begin init_session')
	session = boto3.session.Session(profile_name=CONF_VALUES['AWS_PROFILE'])
	logging.info('End init_session')
	print_event_log('End init_session')

	return session

'''Create aws security group'''
def create_security_group(ec2_client, security_group, sg_rules):
	security_group = ec2_client.create_security_group(
				DryRun=False,
				GroupName=CONF_VALUES['EC2_SG_NAME'],
				Description=CONF_VALUES['EC2_SG_DESC'],
				VpcId=CONF_VALUES['EC2_VPC_ID'])
	logging.info('Security Group id ==> %s' % security_group['GroupId'])
	print_event_log('Security Group id ==> %s' % security_group['GroupId'])
	sg_group_id = security_group['GroupId']
	for sg in sg_rules:
		# Split string on space
		sg_params = sg.split()	
		flag_in_out = sg_params[0]
		ip_protocol = sg_params[1]
		from_port = int(sg_params[2])
		to_port = int(sg_params[3])
		cidr_ip = sg_params[4]
		if flag_in_out == 'Inbound':
			ec2_client.authorize_security_group_ingress(
				DryRun=False,
				GroupId=sg_group_id,
				IpProtocol=ip_protocol,
				FromPort=from_port,
				ToPort=to_port,
				CidrIp=cidr_ip,
			)
		#elif flag_in_out == 'Outbound':
			# Set our Outbound rule
		#	ec2_client.authorize_security_group_egress(
		#		DryRun=False,
		#		GroupId=sg_group_id,
		#		IpPermissions=[
		#			{
		#				'IpProtocol': ip_protocol,
		#				'FromPort': from_port,
		#				'ToPort': to_port,
		#				'IpRanges': [
		#					{'CidrIp': cidr_ip}
		#				]
		#			}
		#		]
		#	)
			# Remove default Outbound rule that allows all traffic
			# aka : allow all to 0.0.0.0/0
		#	ec2_client.revoke_security_group_egress(
		#		DryRun=False,
		#		GroupId=sg_group_id,
		#		IpPermissions=[
		#			{
		#				'IpProtocol': '-1',
		#				'FromPort': -1,
		#				'ToPort': -1,
		#				'IpRanges': [
		#					{'CidrIp': '0.0.0.0/0'}
		#				]
		#			}
		#		]
		#	)
	
	return sg_group_id

'''Craete an ec2 instance'''
def create_ec2_inst(ec2_resource, ec2_client, security_group_id):
	response = ec2_client.run_instances(
		DryRun=False,
		ImageId=CONF_VALUES['EC2_AMI'],
		MinCount=1,
		MaxCount=1,
		KeyName=CONF_VALUES['EC2_KEYPAIR'],
		UserData=CONF_VALUES['EC2_USER_DATA'],
		InstanceType=CONF_VALUES['EC2_INST_TYPE'],
		Placement={
			'AvailabilityZone': CONF_VALUES['EC2_AZ'],
			'Tenancy': 'default'
		},
		BlockDeviceMappings=[
			{
				'DeviceName': '/dev/xvda',
				'Ebs': {
					'VolumeSize': int(\
						CONF_VALUES['EC2_VOLUME_SIZE']),
					'DeleteOnTermination': True,
					'VolumeType': \
						CONF_VALUES['EC2_VOLUME_TYPE'],
				},
			},
		],
		Monitoring={
			'Enabled': True
		},
		NetworkInterfaces=[
			{
				'DeviceIndex': 0,
				'SubnetId': CONF_VALUES['EC2_SUBNET_ID'],
				'PrivateIpAddress': CONF_VALUES['EC2_PRIV_IP'],
				'Groups': [
					security_group_id,
				],
				'AssociatePublicIpAddress':\
					CONF_VALUES['EC2_HAS_PUB_IP'] == 'True'
			},
		],
		IamInstanceProfile={
			#'Arn': 'IamProfileArn',
			'Name': CONF_VALUES['EC2_IAM_ROLE']
		},
	)

	# Get instance id
	instance_id = response['Instances'][0]['InstanceId']
	logging.info('Launched instance with id %s' % instance_id)
	print_event_log('Launched instance with id %s' % instance_id)
	# Wait for the instance to enter the running state
	logging.info('Wait for running to be complete')	
	print_event_log('Wait for running to be complete')	
	waiter = ec2_client.get_waiter('instance_running')
	waiter.wait(
		DryRun=False,
		InstanceIds=[
			instance_id
		]
	)
	if CONF_VALUES['EC2_HAS_PUB_IP'] == 'True':
		public_ip = ec2_resource.Instance(instance_id).public_ip_address
		logging.info("Instance is running. You can connect via " \
				"ssh -i %s.pem admin@%s" \
				%(CONF_VALUES['EC2_KEYPAIR'], public_ip))
		print_event_log("Instance is running. You can connect via " \
				"ssh -i %s.pem admin@%s" \
				%(CONF_VALUES['EC2_KEYPAIR'], public_ip))
	else:
		logging.info("Instance is running. You can connect to it " \
				"from your bastion via ssh -i %s.pem admin@%s" \
				%(CONF_VALUES['EC2_KEYPAIR'], \
					CONF_VALUES['EC2_PRIV_IP']))

	# Tag our instance
	ec2_client.create_tags(
		DryRun=False,
		Resources=[
			instance_id
		],
		Tags=[
			{
				'Key': 'Name',
				'Value': CONF_VALUES['NAME_TAG']
			},
			{
				'Key': 'Env',
				'Value': CONF_VALUES['ENV_TAG']
			}
		]
	)

# Script entry point
if __name__ == '__main__':
	try:
		init_log_file(LOG_FILE)
		logging.info('Aws EC2 creation begin')
		print_event_log('Aws EC2 creation begin')
		get_conf(CONF_FILE)
		dump_conf()
		session = init_session()
		# Getting an ec2 client
		ec2_resource = session.resource('ec2')
		ec2_client = ec2_resource.meta.client
		security_group = None
		# Create security groups
		sg_rules = CONF_VALUES['EC2_SG_RULES'].split(',')
		sg_id = create_security_group(ec2_client, security_group, \
				sg_rules)
		#  Create our instance
		create_ec2_inst(ec2_resource, ec2_client, sg_id)

	except Exception as e:
		# Log the exception
		logging.info('Got this error %s' % e)
		print_event_log('Got this error %s' % e)

