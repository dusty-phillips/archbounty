from django.db import models
from django.contrib.auth.models import User

class PercentageField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {'min_value': 0, 'max_value':100}
        defaults.update(kwargs)
        return super(PercentageField, self).formfield(**defaults)

make_choice = lambda x: (x,x)

class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    status = models.CharField(max_length=6, choices=make_choice("pending",
        "accepted", "completed", "paid"))

class Donation(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, related_name='donations')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=6,
           choices=make_choice("unpaid", "paid"))
    deadline = models.DateTimeField(nullable=True, blank=True, default=None)

class Contibution(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, related_name='contributions')
    percentage = PercentageField()
    description = models.TextField()
