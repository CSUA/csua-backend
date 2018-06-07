from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
from os import popen
import hashlib
import string
from base64 import b64encode
from random import choice

LDAP_SERVER = "ldaps://ldap.csua.berkeley.edu"
LDAP_USER = "uid=newuser,ou=People,dc=csua,dc=berkeley,dc=edu"
LDAP_PASSWORD = ""

def GetLdapPassword():
    global LDAP_PASSWORD
    if LDAP_PASSWORD:
        return LDAP_PASSWORD
    with open('/etc/secrets/newuser.secret') as f:
        LDAP_PASSWORD = f.read().strip()
    return LDAP_PASSWORD

def GetMaxUID():
    return int(popen("ldapsearch -x 'UIDNumber' | grep uidNumber | awk '{print $2}' | sort -n | tail -n 1").read()) + 1

def MakePassword(password):
    salt = ''.join(choice(string.ascii_letters + string.digits) for _ in range(4))
    ctx = hashlib.sha1(password.encode('utf-8'))
    ctx.update(salt.encode('utf-8'))
    return "{SSHA}" + b64encode( ctx.digest() + salt.encode('utf-8') ).decode('utf-8')

def NewUser(username, name, email, sid, password):
    assert(isinstance(username, str))
    assert(isinstance(name, str))
    assert(isinstance(email, str))
    assert(isinstance(sid, int))
    assert(isinstance(password, str))
    s = Server(LDAP_SERVER, get_info=ALL)
    uid = -1
    c = Connection(s, user=LDAP_USER, password=GetLdapPassword())
    if c.bind():
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
            'gecos': '{0},{1}'.format(name, email),
            'loginshell': '/bin/bash',
            }
        c.add(dn, attributes=attrs)
        c.unbind()
        return True, uid
    c.unbind()
    return False, uid

def DeleteUser(username):       #never used
    s = Server(LDAP_SERVER, get_info=ALL)
    c = Connection(s, user=LDAP_USER, password=GetLdapPassword())
    deleteDN = "uid={0},ou=People,dc=csua,dc=berkeley,dc=edu".format(username)
    if c.bind():
        c.delete(deleteDN)
    c.unbind()

def Authenticate(username, password):
    user_dn = "uid={0},ou=people,dc=csua,dc=berkeley,dc=edu".format(username)
    base_dn = "dc=csua,dc=berkeley,dc=edu"
    s = Server(LDAP_SERVER, get_info=ALL)
    search_filter = "(uid="+username + ")"
    c = Connection(s, user=user_dn, password=password)
    if c.bind():
        c.search(base_dn, search_filter)
        c.unbind()
        return True
    c.unbind()
    return False

def IsOfficer(username):
    base_dn = "dc=csua,dc=berkeley,dc=edu"
    s = Server(LDAP_SERVER, get_info=ALL)
    search_filter = "(cn=officers)"
    c = Connection(s, user=LDAP_USER, password = GetLdapPassword())
    if c.bind():
        c.search(base_dn, search_filter, attributes=ALL_ATTRIBUTES)
        result = c.response
        c.unbind()
        officers = result[0]['attributes']['memberUid']
        return username in officers
    c.unbind()

def ValidateOfficer(username, password):
    return IsOfficer(username) and Authenticate(username, password)
