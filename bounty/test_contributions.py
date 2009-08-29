from bounty.forms import ContributionForm

def test_form():
    form = ContributionForm()
    assert len(form.fields) == 2

