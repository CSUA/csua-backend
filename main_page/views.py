from django.http import HttpResponse
from django.template import RequestContext, loader

def constitution(request):
    template = loader.get_template("constitution.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def sponsors(request):
    template = loader.get_template("sponsors.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def events(request):
    template = loader.get_template("events.html")
    context = RequestContext(request, {"events": []})
    return HttpResponse(template.render(context))

def index(request):
    template = loader.get_template("index.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def industry(request):
    template = loader.get_template("industry.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def join(request):
    template = loader.get_template("join.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def hackathon13(request):
    template = loader.get_template("hackathonfa13.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
  
def hackathon14(request):
    template = loader.get_template("hackathonfa14.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def hackathonsp15(request):
    template = loader.get_template("hackathonsp15.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def hackathonfa15(request):
    template = loader.get_template("hackathonfa15.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def hackathonsp16(request):
    template = loader.get_template("hackathonsp16.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def hackathonfa16(request):
    template = loader.get_template("hackathonfa16.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
