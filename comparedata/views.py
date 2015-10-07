from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic.detail import View
from django.views.generic.edit import FormView
from django.conf import settings
from comparedata.forms import JobForm
from comparedata.models import Job, Org, Object, ObjectField, ObjectFieldJob
from django.http import HttpResponse, HttpResponseRedirect
from comparedata.tasks import get_objects_task, get_fields_task

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

		return HttpResponseRedirect('/query-objects/' + str(job.random_id))

	
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


class QueryObjects(View):
	"""
		Query Objects loading page
	"""

	template_name = 'query_objects.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):

		job = get_object_or_404(Job, random_id = self.kwargs['job_id'])

		if job.status == 'Not Started':

			job.status = 'Downloading Objects'
			job.save()

			# Begin download of objects and fields
			get_objects_task.delay(job)

		elif job.status == 'Finished':

			return HttpResponseRedirect('/select-object/' + str(job.random_id) + '/')

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
def get_fields(request, job_id):

	# Query for the job record
	job = get_object_or_404(Job, random_id = job_id)

	# The selected object from the page
	selected_object = json.loads(request.POST.get('object'))

	# Create new job record
	field_job = ObjectFieldJob()
	field_job.job = job
	field_job.object = Object.objects.get(job=job, api_name=selected_object)
	field_job.status = 'Not Started'
	field_job.save()

	# Execute the job
	get_fields_task.delay(job, field_job)

	# Return the id of the job for status checking and processing as required
	return HttpResponse(field_job.id)


# AJAX endpoint to get the status of a get_fields job
def get_fields_job_status(request, field_job_id):

	get_fields_job = get_object_or_404(ObjectFieldJob, id = field_job_id)

	response_data = {
		'status': get_fields_job.status,
		'error': get_fields_job.error
	}

	return HttpResponse(json.dumps(response_data), content_type = 'application/json')


