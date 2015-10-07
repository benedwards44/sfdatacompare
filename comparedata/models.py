from django.db import models


class Job(models.Model):
	"""
		Object to handle a job and relevant settings
	"""

	random_id = models.CharField(db_index=True,max_length=255, blank=True)
	created_date = models.DateTimeField(null=True,blank=True)
	finished_date = models.DateTimeField(null=True,blank=True)
	status = models.CharField(max_length=255, blank=True)
	error = models.TextField(blank=True)

	def sorted_orgs(self):
		return self.org_set.order_by('org_number')

	def sorted_objects(self):
		return self.object_set.order_by('label')


class Org(models.Model):
	"""
		Object to hold org information for a job
	"""

	job = models.ForeignKey(Job, blank=True, null=True)
	org_number = models.PositiveSmallIntegerField()
	access_token = models.CharField(max_length=255)
	instance_url = models.CharField(max_length=255)
	org_id = models.CharField(max_length=255)
	org_name = models.CharField(max_length=255, blank=True)
	username = models.CharField(max_length=255, blank=True)
	status = models.CharField(max_length=255, blank=True)
	error = models.TextField(blank=True)


class Object(models.Model):
	"""
		Object to hold the defaults of a Salesforce object
	"""

	job = models.ForeignKey(Job)
	label = models.CharField(max_length=255)
	api_name = models.CharField(max_length=255)

	def sorted_fields(self):
		return self.objectfield_set.order_by('label')


class ObjectField(models.Model):
	"""
		Object which holds the list of fields for the comparison
	"""

	object = models.ForeignKey(Object)
	label = models.CharField(max_length=255)
	api_name = models.CharField(max_length=255)


class ObjectFieldJob(models.Model):
	"""
		Object to hold a job for the downloading a fields for an object
	"""

	job = models.ForeignKey(Job)
	object = models.ForeignKey(Object)
	status = models.CharField(max_length=255, blank=True)
	error = models.TextField(blank=True)
