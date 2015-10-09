from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic.detail import View
from django.views.generic.edit import FormView
from django.conf import settings
from comparedata.forms import JobForm
from comparedata.models import Job, Org, Object, ObjectField, UnmatchedRecord
from django.http import HttpResponse, HttpResponseRedirect
from comparedata.tasks import get_objects_task, compare_data_task

import sys
import datetime
import uuid
import requests
import json	

reload(sys)
sys.setdefaultencoding("utf-8")


class IndexView(FormView):
	"""
		Home Page Controller
	"""

	template_name = 'index.html'
	form_class = JobForm

	# When view is called via GET
	def get(self, request, *args, **kwargs):
		
		return render(request, self.template_name, {
			'client_id': settings.SALESFORCE_CONSUMER_KEY,
			'redirect_uri': settings.SALESFORCE_REDIRECT_URI
		})

	# Valid form posting
	def form_valid(self, form):

		# Create the job record
		job = Job()
		job.random_id = uuid.uuid4()
		job.created_date = datetime.datetime.now()
		job.status = 'Not Started'
		job.save()

		# Create org one record
		org_one = Org.objects.get(pk = form.cleaned_data['org_one'])
		org_one.job = job
		org_one.save()

		# Create org two record
		org_two = Org.objects.get(pk = form.cleaned_data['org_two'])
		org_two.job = job
		org_two.save()

		return HttpResponseRedirect('/loading/' + str(job.random_id))

	
class OAuthResponse(View):
	"""
		OAuth Response Controller
	"""

	template_name = 'oauth_response.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):

		oauth_code = request.GET.get('code')
		environment = request.GET.get('state')[:-4]
		org_choice = request.GET.get('state')[-4:]
		access_token = ''
		instance_url = ''
		org_id = ''
		error_exists = False
		error_message = ''
		username = ''
		email = ''
		org_name = ''
		org = Org()

		if 'Production' in environment:

			login_url = 'https://login.salesforce.com'
			
		else:

			login_url = 'https://test.salesforce.com'
		
		r = requests.post(
			login_url + '/services/oauth2/token', 
			headers={
				'content-type':'application/x-www-form-urlencoded'
			}, 
			data={
				'grant_type':'authorization_code',
				'client_id': settings.SALESFORCE_CONSUMER_KEY,
				'client_secret': settings.SALESFORCE_CONSUMER_SECRET,
				'redirect_uri': settings.SALESFORCE_REDIRECT_URI,
				'code': oauth_code
			}
		)

		auth_response = json.loads(r.text)

		if 'error_description' in auth_response:

			error_exists = True
			error_message = auth_response['error_description']

		else:

			access_token = auth_response['access_token']
			instance_url = auth_response['instance_url']
			user_id = auth_response['id'][-18:]
			org_id = auth_response['id'][:-19]
			org_id = org_id[-18:]

			# get username of the authenticated user
			r = requests.get(
				instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/User/' + user_id + '?fields=Username,Email', 
				headers={
					'Authorization': 'OAuth ' + access_token
				}
			)
			
			if 'errorCode' in r.text:

				error_exists = True
				error_message = r.json()[0]['message']

			else:

				username = r.json()['Username']
				email = r.json()['Email']

				# get the org name of the authenticated user
				r = requests.get(
					instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/Organization/' + org_id + '?fields=Name', 
					headers={
						'Authorization': 'OAuth ' + access_token
					}
				)
				
				if 'errorCode' in r.text:

					error_exists = True
					error_message = r.json()[0]['message']

				else:

					org_name = r.json()['Name']

					org = Org()
					org.access_token = access_token
					org.instance_url = instance_url
					org.org_id = org_id
					org.org_name = org_name
					org.username = username
					
					if org_choice == 'org1':

						org.org_number = 1

					else:

						org.org_number = 2

					org.save()
		
		return render(request, self.template_name, {
			'client_id': settings.SALESFORCE_CONSUMER_KEY,
			'redirect_uri': settings.SALESFORCE_REDIRECT_URI,
			'error': error_exists, 
			'error_message': error_message, 
			'username': username, 
			'org_name': org_name, 
			'org_choice': org_choice, 
			'org': org, 
			'email': email, 
			'instance_url': instance_url
		})


class LoadingPage(View):
	"""
		Generic loading page for async jobs
	"""

	template_name = 'loading.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):

		job = get_object_or_404(Job, random_id = self.kwargs['job_id'])

		if job.status == 'Not Started':

			job.status = 'Start Object Download'
			job.save()

			# Begin download of objects and fields
			get_objects_task.delay(job)

		elif job.status == 'Objects Downloaded':

			return HttpResponseRedirect('/select-object/' + str(job.random_id) + '/')

		elif job.status == 'Finished':

			return HttpResponseRedirect('/compare-data-result/' + str(job.random_id) + '/')

		return render(request, self.template_name, {
			'job': job
		})


class SelectObject(View):
	"""
		Select Object Controller
	"""

	template_name = 'select_object.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):

		job = get_object_or_404(Job, random_id = self.kwargs['job_id'])

		return render(request, self.template_name, {
			'job': job
		})


class CompareDataResult(View):
	"""
		The compare data result controller
	"""

	template_name = 'compare_data_result.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):

		job = get_object_or_404(Job, random_id = self.kwargs['job_id'])

		return render(request, self.template_name, {
			'job': job
		})


# AJAX endpoint for page to constantly check if job is finished
def job_status(request, job_id):

	# Query for the job record
	job = get_object_or_404(Job, random_id = job_id)

	response_data = {
		'status': job.status,
		'error': job.error
	}

	return HttpResponse(json.dumps(response_data), content_type = 'application/json')


# Endpoint called from AJAX to trigger field query for an object
def get_fields(request, job_id, object_id):

	# Query for the job record
	job = get_object_or_404(Job, random_id = job_id)
	object = get_object_or_404(Object, pk = object_id)

	# If the fields already exist
	if object.sorted_fields():

		# Field list
		fields = []

		# Iterate over the stored fields
		for field in object.sorted_fields():

			# Append to return list
			fields.append({
				'id': field.id,
				'label': field.label,
				'api_name': field.api_name,
				'type': field.type
			})

		# Return the list of fields to the page
		return HttpResponse(json.dumps(fields), content_type = 'application/json')

	# Otherwise, need to query for them via api
	else:

		# List of fields to query
		field_list = []

		# The orgs used for querying
		org_one = job.sorted_orgs()[0]
		org_two = job.sorted_orgs()[1]

		try:

			# Query for Org One fields
			org_one_fields = requests.get(
				org_one.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/' + object.api_name + '/describe/', 
				headers={
					'Authorization': 'Bearer ' + org_one.access_token, 
					'content-type': 'application/json'
				}
			)

			# If there was an error with the request
			if org_one_fields.status_code != 200:

				# Set response data for page
				response_data = {
					'error': True,
					'errorMessage': 'Error querying fields for Org One\n\n' + org_one_fields.json()[0]['errorCode'] + ': ' + org_one_fields.json()[0]['message']
				}

				return HttpResponse(json.dumps(response_data), content_type = 'application/json')

			# Loop through the org one fields
			for field in org_one_fields.json()['fields']:
				field_list.append(field['name'])

			# Query for Org 2 fields
			org_two_fields = requests.get(
				org_two.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/' + object.api_name + '/describe/', 
				headers={
					'Authorization': 'Bearer ' + org_two.access_token, 
					'content-type': 'application/json'
				}
			)

			# If there was an error with the request
			if org_two_fields.status_code != 200:

				# Set response data for page
				response_data = {
					'error': True,
					'errorMessage': 'Error querying fields for Org One\n\n' + org_two_fields.json()[0]['errorCode'] + ': ' + org_two_fields.json()[0]['message']
				}

				return HttpResponse(json.dumps(response_data), content_type = 'application/json')

			# Field list
			fields = []

			# Loop through the org twp fields
			for field in org_two_fields.json()['fields']:
				
				# If the field exists in the set
				if field['name'] in field_list:

					# Create field
					new_field = ObjectField()
					new_field.object = object
					new_field.api_name = field['name']
					new_field.label = field['label']

					# Determine the field type

					# If a formula field, set to formula and add the return type in brackets
					if 'calculated' in field and (field['calculated'] == True or field['calculated'] == 'true'):
						new_field.type = 'Formula (' + field['type'].title() + ')'

					# lookup field
					elif field['type'] == 'reference':

						new_field.type = 'Lookup ('

						# Could be a list of reference objects
						for referenceObject in field['referenceTo']:
							new_field.type = new_field.type + referenceObject.title() + ', '

						# remove trailing comma and add closing bracket
						new_field.type = new_field.type[:-2]
						new_field.type = new_field.type + ')'

					else:
						new_field.type = field['type'].title()

					new_field.save()

			# Re-query fields to sort alphabetically
			for field in ObjectField.objects.filter(object = object).order_by('label'):

				# Append to return list
				fields.append({
					'id': field.id,
					'label': field.label,
					'api_name': field.api_name,
					'type': field.type
				})

			# Return the list of fields to the page
			return HttpResponse(json.dumps(fields), content_type = 'application/json')

		except:

			# Set response data for page
			response_data = {
				'error': True,
				'errorMessage': traceback.format_exc()
			}

			return HttpResponse(json.dumps(response_data), content_type = 'application/json')


# AJAX endpoint to execute the data compare job
def execute_data_compare(request, job_id, object_id):

	# Query for the job and object
	job = get_object_or_404(Job, random_id = job_id)
	object = get_object_or_404(Object, pk = object_id)

	# If POST request made
	if request.method == 'POST':

		# Parse POST data into array
		fields = json.loads(request.body)

	else:

		# Get the fields from the job
		fields = job.fields.split(',')

	# Update the status
	job.status = 'Begin Data Compare'
	job.save()

	# Execute the job
	compare_data_task.delay(job, object, fields)

	# Return the URL to the page
	return HttpResponse('/loading/' + str(job.random_id) + '/')


# AJAX endpoint to get unmatched rows for a job and org
def get_unmatched_rows(request, job_id, org_no):

	# Query for the job and object
	job = get_object_or_404(Job, random_id = job_id)

	# List of records to return
	#unmatched_records = job.sorted_orgs()[org_no].unmatched_records().values_list('data', flat=True)
	unmatched_records = job.sorted_orgs()

	# Return records to page
	#return HttpResponse(json.dumps(unmatched_records), content_type = 'application/json')
	return HttpResponse(unmatched_records)

	
