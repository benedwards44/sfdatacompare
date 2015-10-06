from django import forms

class JobForm(forms.Form):
	"""
		Form to handle the creation of a job
	"""
	org_one = forms.IntegerField(required=False)
	org_two = forms.IntegerField(required=False)