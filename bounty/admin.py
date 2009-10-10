from django.contrib import admin
from bounty.models import Project, Donation, Contribution, Notification

admin.site.register(Project)
admin.site.register(Donation)
admin.site.register(Contribution)
admin.site.register(Notification)
