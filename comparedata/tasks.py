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

@app.task
def get_objects_and_fields(job): 


	job.status = 'Finished'
	job.save()

	"""
	instance_url = schema.instance_url
	org_id = schema.org_id
	access_token = schema.access_token

	# List of standard objects to include
	standard_objects = (
		'Account',
		'AccountContactRole',
		'Activity',
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
		'PartnerRole',
		'Pricebook2',
		'PricebookEntry',
		'Product2',
		'Quote',
		'QuoteLineItem',
		'Solution',
		'Task',
		'User',
	)

	# Describe all sObjects
	all_objects = requests.get(
		instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/', 
		headers={
			'Authorization': 'Bearer ' + access_token, 
			'content-type': 'application/json'
		}
	)

	try:

		if 'sobjects' in all_objects.json():

			for sObject in all_objects.json()['sobjects']:

				if sObject['name'] in standard_objects or sObject['name'].endswith('__c'):

					# Create object record
					new_object = Object()
					new_object.schema = schema
					new_object.api_name = sObject['name']
					new_object.label = sObject['label']
					new_object.save()

					# query for fields in the object
					all_fields = requests.get(instance_url + sObject['urls']['describe'], headers={'Authorization': 'Bearer ' + access_token, 'content-type': 'application/json'})

					# Loop through fields
					for field in all_fields.json()['fields']:

						# Create field
						new_field = Field()
						new_field.object = new_object
						new_field.api_name = field['name']
						new_field.label = field['label']

						if 'inlineHelpText' in field:
							new_field.help_text = field['inlineHelpText']

						# If a formula field, set to formula and add the return type in brackets
						if 'calculated' in field and (field['calculated'] == True or field['calculated'] == 'true'):
							new_field.data_type = 'Formula (' + field['type'] + ')'

						# lookup field
						elif field['type'] == 'reference':

							new_field.data_type = 'Lookup ('

							# Could be a list of reference objects
							for referenceObject in field['referenceTo']:
								new_field.data_type = new_field.data_type + referenceObject.title() + ', '

							# remove trailing comma and add closing bracket
							new_field.data_type = new_field.data_type[:-2]
							new_field.data_type = new_field.data_type + ')'

						# picklist values
						elif field['type'] == 'picklist' or field['type'] == 'multipicklist':

							new_field.data_type = field['type'].title() + ' ('

							# Add in picklist values
							for picklist in field['picklistValues']:
								new_field.data_type = new_field.data_type + picklist['label'] + ', '

							# remove trailing comma and add closing bracket
							new_field.data_type = new_field.data_type[:-2]
							new_field.data_type = new_field.data_type + ')'

						# if text field, add field length
						elif field['type'] == 'string' or field['type'] == 'textarea':

							new_field.data_type = field['type'].title()

							# Add the field length to the title
							if 'length' in field:
								new_field.data_type += ' (' + str(field['length']) + ')'

						# If number, currency or percent
						elif field['type'] == 'double' or field['type'] == 'percent' or field['type'] == 'currency':

							new_field.data_type = field['type'].title()

							# Add the length and precision
							if 'precision' in field and 'scale' in field:

								# Determine the length
								length = int(field['precision']) - int(field['scale'])

								# Add length and scale to the field type
								new_field.data_type += ' (' + str(length) + ',' + str(field['scale']) + ')'

						else:
							new_field.data_type = field['type'].title()

						new_field.save()

			schema.status = 'Finished'

		else:

			schema.status = 'Error'
			schema.error = 'There was no objects returned from the query'

			debug = Debug()
			debug.debug = all_objects.text
			debug.save()

	except Exception as error:
		schema.status = 'Error'
		schema.error = traceback.format_exc()
	
	schema.finished_date = datetime.datetime.now()
	schema.save()
	"""
