from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from bounty.forms import ProjectForm, ProjectStatusForm
from bounty.models import Project

def index(request):
    return render_to_response('index.html', RequestContext(request, {}))

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
    return render_to_response('view_project.html', RequestContext(
        request, page_dict))

def change_project_status(request, project_id):
    if not request.user.has_perm('project.can_change_status'):
        return HttpResponse('not permitted', '403 forbidden')
    project = get_object_or_404(Project, id=project_id)
    form = ProjectStatusForm(instance=project, data=request.POST)
    form.save()
    return HttpResponse(form.instance.status)


def list_projects(request, project_status=None):
    projects = Project.objects.all().order_by('status', '-creation_date')
    if project_status:
        projects = projects.filter(status=project_status)

    return render_to_response("project_list.html", RequestContext(request, 
        {'projects': projects}))
