from django import forms
from bounty.models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('status',)
