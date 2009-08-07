import os, sys
sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from django.test.client import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command

def pytest_funcarg__django_client(request):
    old_name = settings.DATABASE_NAME
    def setup():
        setup_test_environment()
        settings.DEBUG = False
        from django.db import connection
        connection.creation.create_test_db(1, True)
        return Client()
    def teardown(client):
        teardown_test_environment()
        from django.db import connection
        connection.creation.destroy_test_db(old_name, 1)
    return request.cached_setup(setup, teardown, "session")

def pytest_funcarg__client(request):
    def setup():
        return request.getfuncargvalue('django_client')
    def teardown(client):
        call_command('flush', verbosity=0, interactive=False)
    return request.cached_setup(setup, teardown, "function")
