from django.shortcuts import render
from google_currency import convert

# Create your views here.
from all_time_high.models import AllTimeHighRate


def one_page_view(request):
    template = "one_page_template.html"
    content = dict()
    rates = AllTimeHighRate.objects.all()
    for rate in rates:
        content = rate.__dict__

    return render(request, template, context=content)
