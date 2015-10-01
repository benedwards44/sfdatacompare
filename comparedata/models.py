from django.db import models

class Job(models.Model):
	"""
		Object to handle a job and relevant settings
	"""

	random_id = models.CharField(db_index=True,max_length=255, blank=True)
	created_date = models.DateTimeField(null=True,blank=True)
	finished_date = models.DateTimeField(null=True,blank=True)
	password = models.CharField(max_length=255, blank=True)
	email_result = models.BooleanField()
	email = models.CharField(max_length=255,blank=True)
	status = models.CharField(max_length=255, blank=True)
	error = models.TextField(blank=True)

	def sorted_orgs(self):
		return self.org_set.order_by('org_number')


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


