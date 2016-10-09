from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from models import Officer

# Create your views here.
def index(request):
    template = loader.get_template("officers.html")
    officers_all = Officer.objects.order_by('last_name')
    officers = []
    count = 0
    for officer in officers_all:
        if count % 4 == 0:
            officers.append([])
        officers[count / 4].append(officer)
        count += 1
    context = RequestContext(request, {'officers' : officers})
    return HttpResponse(template.render(context))
