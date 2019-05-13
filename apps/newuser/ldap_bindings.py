import hashlib
import string
from base64 import b64encode
from random import choice
from contextlib import contextmanager

from ldap3 import ALL_ATTRIBUTES, SYNC, Connection, Server
from decouple import config


LDAP_SERVER_URL = "ldaps://ldap.csua.berkeley.edu"
LDAP_SERVER = Server(LDAP_SERVER_URL)
LDAP_CLIENT_STRATEGY = SYNC
NEWUSER_DN = "uid=newuser,ou=People,dc=csua,dc=berkeley,dc=edu"
NEWUSER_PW = config("NEWUSER_PW")


@contextmanager
def ldap_connection(**kwargs):
    if "client_strategy" not in kwargs:
        kwargs["client_strategy"] = LDAP_CLIENT_STRATEGY
    else:
        raise RuntimeError(
            "Don't change the client strategy unless you know what you're doing!"
        )
    with Connection(LDAP_SERVER, **kwargs) as c:
        yield c


def get_max_uid():
    with ldap_connection() as conn:
        conn.search(
            "ou=People,dc=csua,dc=berkeley,dc=edu", "(cn=*)", attributes="uidNumber"
        )
        max_uid = max(int(str(entry.uidNumber)) for entry in conn.entries)
        return max_uid


def make_password(password):
    """
    generates a salted SHA-1 hash of the given password
    """
    salt = "".join(choice(string.ascii_letters + string.digits) for _ in range(4))
    ctx = hashlib.sha1(password.encode("utf-8"))
    ctx.update(salt.encode("utf-8"))
    return "{SSHA}" + b64encode(ctx.digest() + salt.encode("utf-8")).decode("utf-8")


def create_new_user(username, name, email, sid, password):
    """
    binds as newuser and creates a new user. be careful that this isn't called by any unpriveleged views.
    """
    with ldap_connection(user=NEWUSER_DN, password=NEWUSER_PW) as c:
        if c.bind():
            dn = "uid={0},ou=people,dc=csua,dc=berkeley,dc=edu".format(username)
            uid = get_max_uid() + 1
            attrs = {
                "uid": username,
                "objectClass": ["account", "posixaccount", "top", "shadowaccount"],
                "homedirectory": "/home/{0}".format(username),
                "uidNumber": str(uid),
                "shadowmax": "99999",
                "gidnumber": "1000",
                "cn": username,
                "shadowwarning": "7",
                "sid": str(sid),
                "userpassword": make_password(password),
                "gecos": "{0},{1}".format(name, email),
                "loginshell": "/bin/bash",
            }
            success = c.add(dn, attributes=attrs)
            return success, uid
        else:
            return False, -1


def authenticate(username, password):
    """
    verifies that the username and password are correct
    """
    user_dn = "uid={0},ou=People,dc=csua,dc=berkeley,dc=edu".format(username)
    with ldap_connection(user=user_dn, password=password) as c:
        if c.bind():
            return True
        else:
            return False


def is_officer(username):
    base_dn = "dc=csua,dc=berkeley,dc=edu"
    search_filter = "(cn=officers)"
    with ldap_connection() as c:
        c.search(base_dn, search_filter, attributes=ALL_ATTRIBUTES)
        officers = c.entries[0].memberUid
        return username in officers


def validate_officer(username, password):
    return is_officer(username) and authenticate(username, password)
