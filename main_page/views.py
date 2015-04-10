from django.http import HttpResponse
from django.template import RequestContext, loader

def about(request):
    template = loader.get_template("about.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def constitution(request):
    template = loader.get_template("constitution.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def donate(request):
    template = loader.get_template("donate.html")
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

def officers(request):
    template = loader.get_template("officers.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def politburo(request):
    template = loader.get_template("politburo.html")
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

def hackathon15(request):
    template = loader.get_template("hackathonsp15.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
