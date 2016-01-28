from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from os import mkdir, chown, system
import ldap_bindings
import pwd

def index(request):
  template = loader.get_template("login.html")
  context = RequestContext(request, {})
  return HttpResponse(template.render(context))

def auth(request):
  if request.method == 'POST':
    username = request.POST.get("username")
    password = request.POST.get("password")
    if ldap_bindings.Authenticate(username,password):
      template = loader.get_template("auth.html")
      context = RequestContext(request, {})
      return HttpResponse(template.render(context))
    else:
      template = loader.get_template("login.html")
      context = RequestContext(request, {'error':'Invalid credentials'})
      return HttpResponse(template.render(context))

def verify(request):
  if request.method == 'POST':
    student_id = request.POST.get("student_id")
    username = request.POST.get("username")

#Password verification? Optional. TBD
    #password = request.POST.get("password")
    #password_confirm = request.POST.get("password_confirm")

    status = ldap_bindings.VerifyUser(str(username), int(student_id))
    print("UID:{0}".format(uid))
    template = loader.get_template("auth.html")
    if not status:
      context = RequestContext(request, {'error':'User validation failed'})
      return HttpResponse(template.render(context))
    context = RequestContext(request, {error: 'User found!'})
    return HttpResponse(template.render(context))
