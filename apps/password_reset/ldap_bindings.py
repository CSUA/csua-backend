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

def make_password(password):
    """
    generates a salted SHA-1 hash of the given password
    """
    salt = "".join(choice(string.ascii_letters + string.digits) for _ in range(4))
    ctx = hashlib.sha1(password.encode("utf-8"))
    ctx.update(salt.encode("utf-8"))
    return "{SSHA}" + b64encode(ctx.digest() + salt.encode("utf-8")).decode("utf-8")

def valid_username_email(username, email):
    user_dn = "uid={0},ou=People,dc=berkeley,dc=edu".format(username)
    search_filter = "(gecos=*{0})".format(email)
    with ldap_connection() as c:
        c.search(user_dn, search_filter, attributes=ALL_ATTRIBUTES)
        users = c.entries[0].memberUid
        return username in users

