import datetime
from django.db import models
from django.contrib.auth.models import User

class PercentageField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {'min_value': 0, 'max_value':100}
        defaults.update(kwargs)
        return super(PercentageField, self).formfield(**defaults)

make_choice = lambda x: ([(p,p) for p in x])

class Project(models.Model):
    class Meta:
        permissions = (
                ('can_change_status', "Can Change Project Status"),
                )
    creator = models.ForeignKey(User)
    name = models.CharField(max_length=64)
    description = models.TextField()
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateField(null=True, blank=True)
    # pending --> user submitted, moderator has not viewed, or is discussing
    # accepted --> moderator deems project acceptable
    # rejected --> moderator deems project unacceptable not worth discussing
    # completed --> users have completed project, but moderator has not
    #               approved the completion
    # paid --> moderator has approved project completion and money is paid out
    status = models.CharField(max_length=16, choices=make_choice(
        ("pending", "accepted", "rejected", "completed", "paid")),
        default="pending")

    def get_absolute_url(self):
        return "/projects/%d/" % self.id

    @property
    def creation_date(self):
        return self.created.date()

    def current_value(self):
        return sum([d.amount for d in self.donations.current()])

    def expired_value(self):
        return sum([d.amount for d in self.donations.expired()])

    def contribution_percentage(self):
        return sum([c.percentage for c in self.contributions.all()])

    def contribution_status(self):
        if self.contribution_percentage < 100:
            return "incomplete"
        elif self.contribution_percentage > 100:
            return "over"
        else:
            return "complete"

    def __unicode__(self):
        return self.name

class DonationManager(models.Manager):
    def paid(self):
        return self.filter(status="paid")

    def unpaid(self):
        return self.filter(status="unpaid")

    def current(self):
        return self.filter(deadline__isnull=True) | self.filter(deadline__gt=datetime.date.today())

    def expired(self):
        return self.filter(deadline__lte=datetime.date.today())

class Donation(models.Model):
    objects = DonationManager()
    user = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='donations')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=6,
           choices=make_choice(("unpaid", "paid")), default="unpaid")
    deadline = models.DateTimeField(null=True, blank=True, default=None)

class Contribution(models.Model):
    user = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='contributions')
    percentage = PercentageField()
    description = models.TextField()

    def get_absolute_url(self):
        return "%scontributions/%d/" % (self.project.get_absolute_url(), self.id)
