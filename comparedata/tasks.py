from __future__ import absolute_import
from celery import Celery
import os
import json	
import ast
import requests
import datetime
import time
import sys
import sqlite3
import StringIO
import glob
import traceback

# Celery config
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfdatacompare.settings')
app = Celery('tasks', broker=os.environ.get('REDIS_URL', 'redis://localhost'))

from django.conf import settings
from comparedata.models import Job, Org, Object, ObjectField

reload(sys)
sys.setdefaultencoding("utf-8")

@app.task
def get_objects_task(job): 
	"""
		Async method to query objects for the given orgs
	"""

	# List of standard objects to include
	standard_objects = (
		'Account',
		'AccountContactRole',
		'Asset',
		'Campaign',
		'CampaignMember',
		'Case',
		'CaseContactRole',
		'Contact',
		'ContentVersion',
		'Contract',
		'ContractContactRole',
		'Event',
		'ForecastingAdjustment',
		'ForecastingQuota',
		'Lead',
		'Opportunity',
		'OpportunityCompetitor',
		'OpportunityContactRole',
		'OpportunityLineItem',
		'Order',
		'OrderItem',
		'Pricebook2',
		'PricebookEntry',
		'Product2',
		'Quote',
		'QuoteLineItem',
		'Solution',
		'Task',
		'User',
	)

	# List to determine if exists in other Org
	object_list = []

	# The orgs used for querying
	org_one = job.sorted_orgs()[0]
	org_two = job.sorted_orgs()[1]

	# Describe all sObjects for the 1st org
	org_one_objects = requests.get(
		org_one.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/', 
		headers={
			'Authorization': 'Bearer ' + org_one.access_token, 
			'content-type': 'application/json'
		}
	)

	try:

		# If sobjects exist in the query (should do)
		if 'sobjects' in org_one_objects.json():

			# Iterate over the JSON response
			for sObject in org_one_objects.json()['sobjects']:

				# If the Org is in the standard list, or is a custom object
				if sObject['name'] in standard_objects or sObject['name'].endswith('__c'):

					# Add object to unique list
					object_list.append(sObject['name'])

					"""
					# query for fields in the object
					all_fields = requests.get(
						org_one.instance_url + sObject['urls']['describe'], 
						headers={
							'Authorization': 'Bearer ' + org_one.access_token, 
							'content-type': 'application/json'
						}
					)

					# Loop through fields
					for field in all_fields.json()['fields']:

						# Add unique field name to the list
						field_list.append(sObject['name'] + '.' + field['name'])
					"""

			org_one.status = 'Finished'

		else:

			org_one.status = 'Error'
			org_one.error = 'There was no objects returned from the query'

	except Exception as error:

		org_one.status = 'Error'
		org_one.error = traceback.format_exc()

	# Now run the process for the 2nd org. Only create object and field records if they exist in both Orgs
	# Describe all sObjects for the 2nd org
	org_two_objects = requests.get(
		org_two.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/', 
		headers={
			'Authorization': 'Bearer ' + org_two.access_token, 
			'content-type': 'application/json'
		}
	)

	try:

		# If sobjects exist in the query (should do)
		if 'sobjects' in org_two_objects.json():

			# Iterate over the JSON response
			for sObject in org_two_objects.json()['sobjects']:

				# If the Org is in the standard list, or is a custom object AND is found in the 1st org
				if (sObject['name'] in standard_objects or sObject['name'].endswith('__c')) and sObject['name'] in object_list:

					# Create object record
					new_object = Object()
					new_object.job = job
					new_object.api_name = sObject['name']
					new_object.label = sObject['label']
					new_object.save()

			org_two.status = 'Finished'

		else:

			org_two.status = 'Error'
			org_two.error = 'There was no objects returned from the query'

	except Exception as error:

		org_two.status = 'Error'
		org_two.error = traceback.format_exc()

	# Save Org 1 and Org 2
	org_one.save()
	org_two.save()

	if org_one.status == 'Error' or org_two.status == 'Error':

		job.status = 'Error'
		job.error = 'There was an error downloading objects and fields for one of the Orgs: \n\n'

		if org_one.error:
			job.error += org_one.error

		if org_two.error:
			job.error += '\n\n' + org_two.error

	else:

		job.status = 'Objects Downloaded'
	
	# Save the job as finished
	job.finished_date = datetime.datetime.now()
	job.save()


@app.task
def compare_data_task(job, object, fields): 
	"""
		Async method to compare the data between selected object and fields
	"""	

	# Update the status
	job.status = 'Comparing Data'
	job.save()

	try:

		# The orgs used for querying
		org_one = job.sorted_orgs()[0]
		org_two = job.sorted_orgs()[1]

		# Set the object against the job
		job.object = object
		job.fields = ', '.join(fields)
		job.object_label = object.label
		job.object_name = object.api_name

		# Build the SOQL query
		soql_query = 'SELECT+' + ','.join(fields) + '+FROM+' + object.api_name

		# Query the 1st org
		org_one_records = requests.get(
			org_one.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/query/?q=' + soql_query, 
			headers={
				'Authorization': 'Bearer ' + org_one.access_token, 
				'content-type': 'application/json'
			}
		)

		if org_one_records.status_code != 200:

			job.status = 'Error'
			job.error = 'There was an error querying records for org one:\n\n' + org_one_records.json()[0]['errorCode'] + ': ' + org_one_records.json()[0]['message'] 

		else:

			# Set the total row count
			job.row_count_org_one = org_one_records.json()['totalSize']

			# Query for the 2nd org
			org_two_records = requests.get(
				org_one.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/query/?q=' + soql_query, 
				headers={
					'Authorization': 'Bearer ' + org_one.access_token, 
					'content-type': 'application/json'
				}
			)

			if org_two_records.status_code != 200:

				job.status = 'Error'
				job.error = 'There was an error querying records for org two:\n\n' + org_two_records.json()[0]['errorCode'] + ': ' + org_two_records.json()[0]['message'] 

			else:

				# Set the total row count
				job.row_count_org_two = org_two_records.json()['totalSize']

				# Determine matching rows

				# Iterate over 1st record
				for org_one_record in org_one_records.json()['records']:

					# Iterate over 2nd record
					for org_two_record in org_two_records.json()['records']:

						pass


				# Set the status to finished
				job.status = 'Finished'

	except:

		job.status = 'Error'
		job.error = traceback.format_exc()

	# Save the job
	job.save()
