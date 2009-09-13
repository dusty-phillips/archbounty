from bounty.models import Donation
from django.conf import settings
import decimal
import datetime

def test_donation_expiry(client, project):
    donation1 = Donation.objects.create(user=project.creator,
            project=project, status="paid", amount="5.00")
    response = client.get(project.get_absolute_url())
    assert "Expired Value" not in response.content

    donation2 = Donation.objects.create(user=project.creator,
            project=project, status="paid", amount="2.00", expire_date=datetime.date.today() - datetime.timedelta(1))

    assert project.current_value() == decimal.Decimal('5.00')
    response = client.get(project.get_absolute_url())
    assert "Expired Value" in response.content
    assert project.expired_value() == decimal.Decimal('2.00')

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
    settings.ALERTPAY_SECURITY_CODE = '1234'
    response = client.post('/alertpayinstnoti/', {
        'ap_securitycode': '1234',
        'ap_status': 'success',
        'ap_itemcode': d.id,
        'ap_amount': 15
        })
    print response.content
    assert response.content == 'received'
    d = Donation.objects.all()[0]
    assert d.status == 'paid'

def test_no_login_cant_donate(client, project):
    project.status = "accepted"
    project.save()
    response = client.get('/projects/%d/' % project.id)
    print response.content
    assert 'Donate' not in response.content
    response = client.post('/projects/%d/donate/' % project.id,
            {'amount': 15})
    assert len(Donation.objects.all()) == 0
