from django.contrib import admin
from comparedata.models import Job, Org, Object, ObjectField

class OrgInline(admin.TabularInline):
	fields = ['org_number','org_name', 'username', 'access_token', 'status', 'error']
	ordering = ['org_number',]
	model = Org
	extra = 0


class JobAdmin(admin.ModelAdmin):
    list_display = ('created_date','finished_date','status','error')
    ordering = ['-created_date']
    inlines = [OrgInline,]


admin.site.register(Job, JobAdmin)
