from django import forms
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(max_length=128, min_length=6)
    password2 = forms.CharField(max_length=128, min_length=6)

    def save(self):
        send_mail('hi', 'hi there', 'dusty@linux.ca', ['dusty@linux.ca'])

    def clean(self):
        data = self.cleaned_data
        if data.get('password1') != data.get('password2'):
            raise forms.ValidationError("The passwords do not match.")

        try:
            User.objects.get(username=data.get('username'))
        except ObjectDoesNotExist:
            pass
        else:
            raise forms.ValidationError(
                    "That username has already been taken.")

        return data
