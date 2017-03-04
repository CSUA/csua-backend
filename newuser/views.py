from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from os import mkdir, system
from . import ldap_bindings

usernameWhitelist = set('.-_')
emailWhitelist = set('@+').union(usernameWhitelist)

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

    try:
      int(student_id)
    except ValueError:
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'Student ID is not a number!'})
      return HttpResponse(template.render(context))

    if (len(student_id) != 8 and len(student_id) != 10):
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'Student ID has incorrect length.'})
      return HttpResponse(template.render(context))

    username = username.lower()
    if not validUsername(username):
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'Invalid username.'})
      return HttpResponse(template.render(context))

    if not validEmail(email):
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'Invalid email address.'})
      return HttpResponse(template.render(context))

    if not validPassword(password):
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'This password does not meet our security requirements.'})
      return HttpResponse(template.render(context))      

    if not ldap_bindings.ValidateOfficer(officer_username, officer_password):
          template = loader.get_template("create_failure.html")
          context = RequestContext(request, {'error':'Officer validation failed.'})
          return HttpResponse(template.render(context))

    enroll_jobs = 'true' if enroll_jobs else "false"

    status, uid = ldap_bindings.NewUser(str(username), str(full_name), str(email), int(student_id), str(password))
    print("UID:{0}".format(uid))
    if not status:
      template = loader.get_template("create_failure.html")
      context = RequestContext(request, {'error':'Your username is already taken.'})
      return HttpResponse(template.render(context))
    system("sudo /webserver/CSUA-backend/newuser/config_newuser {0} {1} {2} {3}".format(username, email, uid, enroll_jobs))
    template = loader.get_template("create_success.html")
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def validUsername(username):
  """
  This helper function takes in a string (the username) and checks if it has whitelisted characters. 
  If there's a character that is not whitelisted, it is not a valid username. In other words, the 
  username must be composed of whitelisted characters. 
  """
  for character in username:
    if not character.isalnum() and character not in usernameWhitelist:
      return False
  return True

def validEmail(email):
  """
  Similar to validUsername, but for emails!
  """
  for character in email:
    if not character.isalnum() and character not in emailWhitelist:
      return False
  return True

def validPassword(password):
  """
  The password must be at least nine characters long. Also, it must include characters from 
  two of the three following categories:
  -alphabetical
  -numerical
  -punctuation/other
  """
  def isNumber(character):
    try:
      int(character)
      return True
    except:
      return False

  punctuation = set("""!@#$%^&*()_+|~-=\`{}[]:";'<>?,./""")
  alpha = False
  num = False
  punct = False
  
  for character in password:
    if character.isalpha():
      alpha = True
    if isNumber(character):
      num = True
    if character in punctuation:
      punct = True
  return (alpha and num) or (alpha and punct) or (num and punct)