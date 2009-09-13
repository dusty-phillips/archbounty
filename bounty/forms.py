from django import forms
from bounty.models import Project, Contribution, Donation

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('status',)

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('amount', 'expire_date')

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('percentage', 'description', 'waive_donations')
