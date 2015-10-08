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

	# Data Compare Results
	object_id = models.PositiveSmallIntegerField(null=True,blank=True)
	object_label = models.CharField(max_length=1000, blank=True)
	object_name = models.CharField(max_length=1000, blank=True)
	fields = models.CharField(max_length=1000, blank=True)
	row_count_org_one = models.IntegerField(null=True,blank=True)
	row_count_org_two = models.IntegerField(null=True,blank=True)
	matching_rows_count_org_one = models.IntegerField(null=True,blank=True)
	matching_rows_count_org_two = models.IntegerField(null=True,blank=True)
	unmatching_rows_count_org_one = models.IntegerField(null=True,blank=True)
	unmatching_rows_count_org_two = models.IntegerField(null=True,blank=True)

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

	def unmatched_records(self):
		return self.unmatchedrecord_set.all()


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
	type = models.CharField(max_length=255)


class UnmatchedRecord(models.Model):
	"""
		Object which holds a record that exists in one Org and not the other 
	"""

	job = models.ForeignKey(Job)
	org = models.ForeignKey(Org)
	data = models.TextField() # The JSON array of fields and field value

