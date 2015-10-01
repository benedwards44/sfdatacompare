from django.shortcuts import render
from django.views.generic.detail import View
from django.conf import settings
from comparedata.forms import JobForm

import sys
import datetime
import uuid

reload(sys)
sys.setdefaultencoding("utf-8")


class IndexView(View):
	"""
		Home Page Controller
	"""

	template_name = 'index.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):
		
		return render(request, self.template_name, {
			'client_id': settings.SALESFORCE_CONSUMER_KEY,
			'redirect_uri': settings.SALESFORCE_REDIRECT_URI,
			'job_form': JobForm()
		})

	# When the form view is posted
	def post(self, request, *args, **kwargs):

		# Get the posted form details
		form = JobForm(request.POST)

		if form.is_valid():

			# Create the job record
			job = Job()
			job.random_id = uuid.uuid4()
			job.created_date = datetime.datetime.now()
			job.status = 'Not Started'
			job.email = form.cleaned_data['email']
			job.save()

			# Create org one record
			org_one = Org.objects.get(pk = form.cleaned_data['org_one'])
			org_one.job = job
			org_one.save()

			# Create org two record
			org_two = Org.objects.get(pk = form.cleaned_data['org_two'])
			org_two.job = job
			org_two.save()

			return HttpResponseRedirect('/run_job/' + str(job.random_id))

		return super(IndexView, self).post(request, *args, **kwargs)



class OAuthResponse(View):
	"""
		OAuth Response Controller
	"""

	template_name = 'oauth_response.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):
		
		return render(request, self.template_name, {
			'client_id': settings.SALESFORCE_CONSUMER_KEY,
			'redirect_uri': settings.SALESFORCE_REDIRECT_URI
		})