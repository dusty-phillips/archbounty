from bounty.models import Project, Donation

def pytest_funcarg__project(request):
    return Project.objects.create(name="Test Project",
            description="This project is a test")

def test_project(client, user, project):
    client.login(username=user.username, password=user.password)
    assert project.status == 'pending'
    response = client.get('/projects/%d/' % project.id)
    assert 'pending' in response.content

def test_change_status(client, admin, project):
    assert admin.has_perm('projects.project.can_change_status')
    assert client.login(username=admin.username, password=admin.username)
    response = client.post('/projects/%d/change_status/' % project.id,
            {'status': 'accepted'})
    print response.content
    assert response.content == 'accepted'
    revised_project = Project.objects.get(id=project.id)
    assert revised_project.status == 'accepted'

def test_unprivleged_no_change_status(client, user, project):
    assert not user.has_perm('projects.project.can_change_status')
    assert client.login(username=user.username, password=user.username)
    response = client.post('/projects/%d/change_status/' % project.id,
            {'status': 'accepted'})
    print response.content
    assert response.content == 'not permitted'
    revised_project = Project.objects.get(id=project.id)
    assert revised_project.status == 'pending'

def test_donation(client, user, project):
    assert client.login(username=user.username, password=user.username)
    assert len(Donation.objects.all()) == 0
    response = client.post('/projects/%d/donate/' % project.id,
            {'amount': '15'})
    assert len(Donation.objects.all()) == 1
    d = Donation.objects.all()[0]
    assert d.amount == 15
    assert d.status == 'unpaid'
    assert d.user == user

    client.logout()
    response = client.post('/alertpayinstnoti/', {
        'ap_securitycode': 'abcdef',
        'ap_status': 'success',
        'ap_itemcode': d.id,
        'ap_amount': 15
        })
    assert response.content == 'received'
    d = Donation.objects.all()[0]
    assert d.status == 'paid'
