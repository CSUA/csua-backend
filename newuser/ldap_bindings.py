import ldap
import ldap.modlist as modlist
from os import popen
import sha
import hashlib
import string
from base64 import b64encode
from random import choice

LDAP_SERVER = "ldap.csua.berkeley.edu"
LDAP_USER = "uid=newuser,ou=People,dc=csua,dc=berkeley,dc=edu"
LDAP_PASSWORD = "newuser"

def GetMaxUID():
    return int(popen("ldapvi --out  | grep uidNumber | awk '{print $2}' | sort -n | tail -n 1").read()) + 1

def MakePassword(password):
    salt = ''.join(choice(string.letters + string.digits) for _ in range(4))
    ctx = sha.new(password)
    ctx.update(salt)
    return "{SSHA}" + b64encode( ctx.digest() + salt )

def NewUser(username, name, email, sid, password):
    assert(type(username) == str)
    assert(type(name) == str)
    assert(type(email) == str)
    assert(type(sid) == int)
    assert(type(password) == str)
    l = ldap.initialize("ldaps://{0}/".format(LDAP_SERVER))
    try:
        l.simple_bind_s(LDAP_USER, LDAP_PASSWORD)
        dn="uid={0},ou=people,dc=csua,dc=berkeley,dc=edu".format(username)
	uid = GetMaxUID()
        attrs = {
            'uid': username,
            'objectclass': ['account', 'posixaccount', 'top', 'shadowaccount'],
            'homedirectory': '/home/{0}'.format(username),
            'uidnumber': str(uid),
            'shadowmax': '99999',
            'gidnumber': '1000',
            'cn': username,
            'shadowwarning': '7',
            'sid': str(sid),
            'userpassword': MakePassword(password),
            'gecos': '{0},{1}'.format(name,email),
            'loginshell': '/bin/bash',
            }
        ldif = modlist.addModlist(attrs)
        l.add_s(dn,ldif)
        l.unbind_s()
        return True, uid
    except Exception as e:
        print e
        l.unbind_s()
        return False, uid

def DeleteUser(username):
    l = ldap.open(LDAP_SERVER)
    l.simple_bind(LDAP_USER, LDAP_PASSWORD)
    deleteDN = "uid={0},ou=People,dc=csua,dc=berkeley,dc=edu".format(username)
    l.delete_s(deleteDN)

def Authenticate(username, password):
    user_dn="uid={0},ou=people,dc=csua,dc=berkeley,dc=edu".format(username)
    base_dn = "dc=csua,dc=berkeley,dc=edu"
    l = ldap.open(LDAP_SERVER)
    search_filter = "uid="+username
    try:
        l.bind_s(user_dn,password)
        result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,search_filter)
        l.unbind_s()
        return True
    except ldap.LDAPError:
        l.unbind_s()
        return False

def IsOfficer(username):
    base_dn = "dc=csua,dc=berkeley,dc=edu"
    l = ldap.open(LDAP_SERVER)
    search_filter = "cn=officers"
    try:
        l.bind_s(LDAP_USER,LDAP_PASSWORD)
        result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,search_filter)
        l.unbind_s()
        officers = result[0][1]['memberUid']
        return username in officers
    except ldap.LDAPError:
        l.unbind_s()
        return False

def ValidateOfficer(username, password):
    return IsOfficer(username) and Authenticate(username, password)
