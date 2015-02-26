from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from os import mkdir, chown, system
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
	status, uid = ldap_bindings.NewUser(str(username), str(full_name), str(email), int(student_id), str(password))
        print "UID:{0}".format(uid)
        if not status:
            template = loader.get_template("create_failure.html")
            context = RequestContext(request, {'error':'Your username is already taken.'})
            return HttpResponse(template.render(context))
        mkdir("/home/{0}".format(username))
        with open("/home/{0}/.forward".format(username),"w") as fd:
            fd.write(email)
	system("ssh root@nfs chown {0} {1}".format(uid, "/nfs/homes/{0}".format(username)))
	system("ssh root@nfs chown {0} {1}".format(uid, "/nfs/homes/{0}/.forward".format(username)))
        #TODO(alchu): If enroll_jobs, enroll user in jobs mailing list.
        #Temporary measure(austin): writing users to a temporary file ("jobs_mailing_list"), to be added manually
        if enroll_jobs:
            try:
                with open("jobs_mailing_list", "a+") as f:
                    f.write(username + " " + email)
            except:
                print "This should never happen (mailing list file does not exist)"
        template = loader.get_template("create_success.html")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
    else:
        template = loader.get_template("create.html")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
