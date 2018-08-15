from os import mkdir, system

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import ldap_bindings

usernameWhitelist = set('.-_')
emailWhitelist = set('@+').union(usernameWhitelist)

def index(request):
  return render(request, 'newuser.html')

@require_POST
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
      return render(request, 'create_failure.html', {'error':'Student ID is not a number!'})

    if (len(student_id) != 8 and len(student_id) != 10):
      return render(request, 'create_failure.html', {'error':'Student ID has incorrect length.'})

    username = username.lower()
    if not validUsername(username):
      return render(request, 'create_failure.html', {'error':'Invalid username.'})

    if not validEmail(email):
      return render(request, 'create_failure.html', {'error':'Invalid email address.'})

    if not validPassword(password):
      return render(request, 'create_failure.html', {'error':'This password does not meet our security requirements. Your password needs to have at least nine characters, and must include characters from two of the three following character classes: alphabetical, numerical, and punctuation/other characters.'})

    if not ldap_bindings.ValidateOfficer(officer_username, officer_password):
      return render(request, 'create_failure.html', {'error':'Officer validation failed.'})

    enroll_jobs = 'true' if enroll_jobs else "false"

    status, uid = ldap_bindings.NewUser(str(username), str(full_name), str(email), int(student_id), str(password))
    print("UID:{0}".format(uid))
    if not status:
      return render(request, 'create_failure.html', {'error':'Your username is already taken.'})
    system("sudo /webserver/CSUA-backend/newuser/config_newuser {0} {1} {2} {3}".format(username, email, uid, enroll_jobs))

    return render(request, 'create_success.html')

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
  punctuation = set("""!@#$%^&*()_+|~-=\`{}[]:";'<>?,./""")
  alpha = False
  num = False
  punct = False

  if len(password) < 9:
    return False
  
  for character in password:
    if character.isalpha():
      alpha = True
    if character.isdigit():
      num = True
    if character in punctuation:
      punct = True
  return (alpha + num + punct) >= 2
