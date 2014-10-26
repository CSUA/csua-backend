from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from os import mkdir, chown
import ldap_bindings
import pwd

def index(request):
    template = loader.get_template("newuser.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def create(request):
    if request.method == 'POST':
        full_name = request.POST.get("full_name")
        student_id = request.POST.get("student_id")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        enroll_jobs = request.POST.get("enroll_jobs") == 'on'
        officer_username = request.POST.get("officer_username")
        officer_password = request.POST.get("officer_password")
        agree_rules = request.POST.get("agree_rules") == 'on'

        if not ldap_bindings.ValidateOfficer(officer_username, officer_password):
            template = loader.get_template("create_failure.html")
            context = RequestContext(request, {'error':'Officer validation failed.'})
            return HttpResponse(template.render(context))
        if not ldap_bindings.NewUser(str(username), str(full_name), str(email), int(student_id), str(password)):
            template = loader.get_template("create_failure.html")
            context = RequestContext(request, {'error':'Your username is already taken.'})
            return HttpResponse(template.render(context))
        mkdir("/home/{0}".format(username))
        chown("/home/{0}".format(username), pwd.getpwnam(username).pw_uid, -1)
        with open("/home/{0}/.forward".format(username),"w") as fd:
            fd.write(email)
        chown("/home/{0}/.forward".format(username), pwd.getpwnam(username).pw_uid, -1)
        #TODO(alchu): If enroll_jobs, enroll user in jobs mailing list.
        template = loader.get_template("create_success.html")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
    else:
        template = loader.get_template("create.html")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
