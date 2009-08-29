from django import forms
from bounty.models import Project, Contribution

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('status',)

class DonationForm(forms.Form):
    amount = forms.DecimalField()

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('percentage', 'description')
