from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from bounty.forms import ProjectForm
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
    project = get_object_or_404(Project, id=project_id)
    return render_to_response('view_project.html', RequestContext(
        request, {'project': project}))
