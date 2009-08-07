from django.contrib.auth.models import User
from django.core import mail
from accounts.forms import RegistrationForm
import py.test

def pytest_generate_tests(metafunc):
    if "invalid_registration" in metafunc.funcargnames:
        # Generate several invalid form inputs
        for invalid in (
                {'username': 'thisusernameiswaaaaaytoooooooolong'*10,
                    'password1': 'p123456',
                    'password2': 'p123456',
                    'email': 'me@example.com'},
                {'username': '',
                    'password1': 'p123456',
                    'password2': 'p123456',
                    'email': 'me@example.com'},
                {'username': 'validname',
                    'password1': 'sh',
                    'password2': 'sh',
                    'email': 'me@example.com'},
                {'username': 'validname',
                    'password1': '',
                    'password2': '',
                    'email': 'me@example.com'},
                {'username': 'validname',
                    'password1': 'p123456',
                    'password2': 'p123456',
                    'email': ''},
                {'username': 'validname',
                    'password1': 'p123456',
                    'password2': 'p123456',
                    'email': 'meeee.com'},
            {   'username': 'test_user',
                'password1': 'p123456',
                'password2': '12p3456',
                'email': 'me@example.com'}
                ):
            metafunc.addcall(funcargs={'invalid_registration': invalid})

def test_registration_page(client):
    response = client.get('/accounts/register/')
    assert isinstance(response.context['form'], RegistrationForm)

    assert 'name="username"' in response.content
    assert 'name="password1"' in response.content

    assert 'registration/register.html' in [t.name for t in response.template]
    assert len(User.objects.all()) == 0

def test_registration_invalid(client, invalid_registration):
    response = client.post('/accounts/register/', invalid_registration)
    assert response.context['form'].errors
    print response.context['form'].errors

def test_registration_makes_email(client):
    response = client.post('/accounts/register/',
            {'username': 'validname',
                'password1': 'pppppp',
                'password2': 'pppppp',
                'email': 'blah@exampl.com'})
    assert len(mail.outbox) == 1

def test_duplicate_registration(client):
    py.test.skip('not implemented')
    raise NotImplementedError()




