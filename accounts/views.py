from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm

@login_required
def profile(request):
    return render_to_response('user_profile.html', RequestContext(request))

def register(request):
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            redirect(reverse('accounts.views.profile'))
    else:
        form = RegistrationForm()
    return render_to_response('registration/register.html',
            RequestContext(request, {'form': form}))
