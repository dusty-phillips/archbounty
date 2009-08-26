from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from bounty.forms import ProjectForm, ProjectStatusForm, DonationForm
from bounty.models import Project, Donation
from django.conf import settings

def index(request):
    return render_to_response('index.html', RequestContext(request, {}))

@login_required
def new_project(request):
    if request.POST:
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(form.instance.get_absolute_url())
    else:
        form = ProjectForm()
    return render_to_response('project_form.html', RequestContext(
        request, {'form': form})) 

def view_project(request, project_id):
    page_dict = {}
    project = get_object_or_404(Project, id=project_id)
    page_dict['project'] = project
    if request.user.has_perm('project.can_change_status'):
        page_dict['status_form'] = ProjectStatusForm(instance=project)
    if request.user.is_authenticated and project.status=="accepted":
        page_dict['donation_form'] = DonationForm()
    return render_to_response('view_project.html', RequestContext(
        request, page_dict))

def change_project_status(request, project_id):
    if not request.POST:
        return HttpResponse("bad method", '405 method not allowed')
    if not request.user.has_perm('project.can_change_status'):
        return HttpResponse('not permitted', '403 forbidden')
    project = get_object_or_404(Project, id=project_id)
    form = ProjectStatusForm(instance=project, data=request.POST)
    form.save()
    return HttpResponse(form.instance.status)

def donate(request, project_id):
    if not request.POST:
        return HttpResponse("bad method", '405 method not allowed')
    if not request.user.is_authenticated():
        return HttpResponse('not permitted', '403 forbidden')
    project = get_object_or_404(Project, id=project_id)
    form = DonationForm(request.POST)
    if form.is_valid():
        donation = Donation()
        donation.user = request.user
        donation.amount = form.cleaned_data['amount']
        donation.project = project
        donation.save()
        return render_to_response("donate.html", RequestContext(
            request, {'amount': form.cleaned_data['amount'],
                'project': project, 'item_code': donation.id}))
    else:
        return render_to_response("form.html", RequestContext(
            request, {'form': form}))

def donation_notify(request): 
    if not request.POST:
        return HttpResponse("bad method", '405 method not allowed')

    if request.POST['ap_securitycode'] != settings.ALERTPAY_SECURITY_CODE:
        return HttpResponse("not permitted", '403 not permitted')

    if request.POST['ap_status'] == 'success':
        donation = get_object_or_404(Donation, id=request.POST['ap_itemcode'],
                amount=request.POST['ap_amount'])
        donation.status = 'paid'
        donation.save()
    
    return HttpResponse("received")

def list_projects(request, project_status=None):
    projects = Project.objects.all().order_by('status', '-creation_date')
    if project_status:
        projects = projects.filter(status=project_status)

    return render_to_response("project_list.html", RequestContext(request, 
        {'projects': projects}))
