from django.shortcuts import render
from django.views.generic.detail import View
from django.conf import settings

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class IndexView(View):
	"""
		Home Page View
	"""

	template_name = 'index.html'

	# When view is called via GET
	def get(self, request, *args, **kwargs):
		
		return render(request, self.template_name, {
			'client_id': settings.SALESFORCE_CONSUMER_KEY,
			'redirect_uri': settings.SALESFORCE_REDIRECT_URI
		})
