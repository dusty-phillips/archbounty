import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.conf import settings
from django.db.models.signals import post_save

from django.core.mail import send_mail

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
    description = models.TextField(help_text='<a href="http://daringfireball.net/projects/markdown/syntax">Markdown</a> syntax is supported.')
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
        return self.filter(expire_date__isnull=True) | self.filter(expire_date__gt=datetime.date.today())

    def expired(self):
        return self.filter(expire_date__lte=datetime.date.today())

class Donation(models.Model):
    objects = DonationManager()
    user = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='donations')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=6,
           choices=make_choice(("unpaid", "paid")), default="unpaid")
    expire_date = models.DateTimeField(null=True, blank=True, default=None)

    def __unicode__(self):
        return "$%s to %s" % (self.amount, self.project)

class Contribution(models.Model):
    user = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='contributions')
    percentage = PercentageField()
    waive_donations = models.BooleanField(default=False)
    description = models.TextField(help_text='<a href="http://daringfireball.net/projects/markdown/syntax">Markdown</a> syntax is supported.')

    def __unicode__(self):
        return "%s to %s" %(self.user, self.project)

    def get_absolute_url(self):
        return "%scontributions/%d/" % (self.project.get_absolute_url(), self.id)

class Notification(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    notify = models.BooleanField(default=False)


def project_notification(sender, instance, signal, created, *args, **kwargs):
    '''when a project is updated or comment is added, send notification e-mails
    to interested users.'''
    if created:
        send_mail("Arch Bounty - New Project Created: %s" % instance.name, "New Project was created", 'bounty@archlinux.ca', [i[1] for i in settings.ADMINS])
    else:
        notifications = instance.notification_set.all()
        to_addresses = [n.user.email for n in notifications]
        send_mail("Arch Bounty Project '%s' updated" % instance.name,
                "The '%s' project at http://%s%s has been updated." % (instance.name, Site.objects.get_current().domain, instance.get_absolute_url()), 'bounty@archlinux.ca', to_addresses)

post_save.connect(project_notification, sender = Project)

def comment_notification(sender, instance, signal, created, *args, **kwargs):
    parent_object = instance.content_object
    while isinstance(parent_object, Comment):
        parent_object = parent_object.content_object
    if isinstance(parent_object, Project):
        notifications = parent_object.notification_set.filter(notify=True)
        to_addresses = [n.user.email for n in notifications]
        send_mail("Arch Bounty Project '%s' commented on" % parent_object.name,
                "The '%s' project has had a new comment added at http://%s%s" % (parent_object.name, Site.objects.get_current().domain, instance.get_absolute_url()), 'bounty@archlinux.ca', to_addresses)
post_save.connect(comment_notification, sender = Comment)
