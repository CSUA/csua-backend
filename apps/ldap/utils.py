"""
Utilities for doing LDAP operations.

Most of these functions create a new connection when called, they should really
be refactored to be methods on a custom Connection object but I am lazy.

--robertquitt
"""
import hashlib
import string
from base64 import b64encode
from contextlib import contextmanager
from datetime import datetime, timedelta
from random import choice

from decouple import config
from django.http import Http404
from ldap3 import (
    ALL_ATTRIBUTES,
    MODIFY_ADD,
    MODIFY_DELETE,
    MODIFY_REPLACE,
    SYNC,
    Connection,
    Server,
)

LDAP_SERVER_URL = "ldaps://ldap.csua.berkeley.edu"
# TODO: make things faster because connect_timeout=2 was too slow (caused socket closure)
LDAP_SERVER = Server(LDAP_SERVER_URL, connect_timeout=10)
LDAP_CLIENT_STRATEGY = SYNC
CSUA_DC = "dc=csua,dc=berkeley,dc=edu"
PEOPLE_OU = "ou=People," + CSUA_DC
GROUP_OU = "ou=Group," + CSUA_DC
NEWUSER_DN = "uid=newuser," + PEOPLE_OU
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


@contextmanager
def newuser_connection(**kwargs):
    """
    creates a connection that binds as newuser, which has edit access to LDAP database
    """
    with ldap_connection(user=NEWUSER_DN, password=NEWUSER_PW, **kwargs) as c:
        yield c


def get_max_uid():
    with ldap_connection() as c:
        c.search(PEOPLE_OU, "(cn=*)", attributes="uidNumber")
        max_uid = max(int(str(entry.uidNumber)) for entry in c.entries)
        return max_uid


def make_password(password):
    """
    generates a salted SHA-1 hash of the given password
    """
    salt = "".join(choice(string.ascii_letters + string.digits) for _ in range(4))
    ctx = hashlib.sha1(password.encode("utf-8"))
    ctx.update(salt.encode("utf-8"))
    return "{SSHA}" + b64encode(ctx.digest() + salt.encode("utf-8")).decode("utf-8")


def change_password(username, new_password):
    # using newuser_connection for edit privileges
    with newuser_connection() as c:
        if c.bind():
            success = c.modify(
                "uid={0},{1}".format(username, PEOPLE_OU),
                {"userpassword": [MODIFY_REPLACE, make_password(new_password)]},
            )
            return success
        else:
            return False


def create_new_user(username, name, email, sid, password):
    """
    binds as newuser and creates a new user. be careful that this isn't called by any unpriveleged views.

    Returns a tuple of (success, uid)

    If uid is -1, this means the bind failed.
    """
    with newuser_connection() as c:
        if c.bind():
            dn = "uid={0},{1}".format(username, PEOPLE_OU)
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


def delete_user(username):
    """Deletes a user. Returns True on successful deletion, False on failed
    deletion, and raises a RuntimeError if newuser fails to bind.
    """
    with newuser_connection() as c:
        if c.bind():
            dn = f"uid={username},{PEOPLE_OU}"
            success = c.delete(dn)
            return success
        else:
            raise RuntimeError("Failed to bind as newuser")


def add_officer(username):
    return add_group_member("officers", username)


def add_group_member(group, username):
    with newuser_connection() as c:
        if c.bind():
            success = c.modify(
                "cn={0},{1}".format(group, GROUP_OU),
                {"memberUid": [(MODIFY_ADD, [username])]},
            )
            if success:
                return True, "Success"
            else:
                return False, "Modify operation failed"
        else:
            return False, "Failed to bind"


def remove_group_members(group, usernames):
    if not usernames:
        # without this check, the memberUid attribute gets overridden with []
        return False, "No users specified"
    with newuser_connection() as c:
        if c.bind():
            success = c.modify(
                "cn={0},{1}".format(group, GROUP_OU),
                {"memberUid": [(MODIFY_DELETE, usernames)]},
            )
            if success:
                return True, "Success"
            else:
                return False, "Modify operation failed"
        else:
            return False, "Failed to bind"


def authenticate(username, password):
    """
    verifies that the username and password are correct
    """
    user_dn = "uid={0},{1}".format(username, PEOPLE_OU)
    with ldap_connection(user=user_dn, password=password) as c:
        if c.bind():
            return True
        else:
            return False


def get_all_groups():
    with ldap_connection() as c:
        c.search(GROUP_OU, "(objectClass=posixGroup)", attributes="cn")
        groups = [str(entry.cn) for entry in c.entries]
        return groups


def get_group_members(group):
    search_filter = "(cn={0})".format(group)
    with ldap_connection() as c:
        c.search(GROUP_OU, search_filter, attributes=ALL_ATTRIBUTES)
        if len(c.entries) == 0:
            raise Http404("No group found")
        if "memberUid" in c.entries[0]:
            return list(c.entries[0].memberUid)
        else:
            return []


def get_root():
    return get_group_members("root")


def get_prosps():
    return get_group_members("prosp-officers")


def get_officers():
    return get_group_members("officers")


def get_politburo():
    return get_group_members("excomm")


def get_user_creation_time(username):
    # WIP
    with ldap_connection() as c:
        c.search(
            PEOPLE_OU,
            "(uid={0})".format(username),
            attributes=[
                "createTimestamp",
                "creatorsName",
                "modifyTimestamp",
                "modifiersName",
            ],
        )
        if len(c.entries) == 0:
            raise Http404("No such user!")

        return [
            str(c.entries[0].createTimestamp),
            str(c.entries[0].creatorsName),
            str(c.entries[0].modifyTimestamp),
            str(c.entries[0].modifiersName),
        ][0]


def get_user_info(username):
    with ldap_connection() as c:
        c.search(PEOPLE_OU, "(uid={0})".format(username), attributes="*")
        if len(c.entries) == 0:
            raise Http404("No such user!")

        return c.entries[0]


def get_user_gecos(username):
    with ldap_connection() as c:
        c.search(PEOPLE_OU, "(uid={0})".format(username), attributes="gecos")
        if len(c.entries) == 0:
            raise Http404("No such user!")

        return str(c.entries[0].gecos)


def get_user_hashed_password(username):
    with newuser_connection() as c:
        c.search(PEOPLE_OU, "(uid={0})".format(username), attributes="userpassword")
        if len(c.entries) == 0:
            raise Http404("No such user!")

        return str(c.entries[0].userpassword)


def user_exists(username):
    with ldap_connection() as c:
        c.search(PEOPLE_OU, "(uid={0})".format(username), attributes="")
        return len(c.entries) == 1


def get_user_realname(username):
    gecos = get_user_gecos(username)
    return gecos.split(",", 1)[0]


def get_user_email(username):
    gecos = get_user_gecos(username)
    gecos_list = gecos.split(",", 1)
    # check if email exists (old entries don't have one)
    if len(gecos_list) < 2:
        return None
    else:
        return gecos_list[1]


def email_exists(email):
    with ldap_connection() as c:
        search_filter = "(gecos=*{0})".format(email)
        c.search(PEOPLE_OU, search_filter, attributes="gecos")
        if len(c.entries) > 0:
            return True
        return False


def get_user_groups(username):
    with ldap_connection() as c:
        c.search(GROUP_OU, "(memberUid={})".format(username), attributes="cn")
        groups = [str(entry.cn) for entry in c.entries]
        return groups


def is_officer(username):
    officers = get_officers()
    return username in officers


def is_root(username):
    root = get_root()
    return username in root


def validate_officer(username, password):
    return is_officer(username) and authenticate(username, password)


def datetime_to_ldap(dt):
    """
    Convert datetime object to LDAP generalized time format
    """
    return dt.strftime("%Y%m%d%H%M%S") + "Z"


def str_to_datetime(s):
    """
    Convert standard date format string to datetime object
    """
    s = s[:-3] + s[-2:]  # remove colon in time zone
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S%z")


def get_members_older_than(days=1460):
    time_threshold = datetime_to_ldap(datetime.now() - timedelta(days=days))
    with ldap_connection() as c:
        c.search(PEOPLE_OU, f"(createTimestamp<={time_threshold})", attributes="cn")
        return [str(entry.cn) for entry in c.entries]


def get_members_in_age_range(min_age_days=0, max_age_days=180):
    assert max_age_days >= min_age_days and min_age_days >= 0, "invalid range"
    min_threshold = datetime_to_ldap(datetime.now() - timedelta(days=min_age_days))
    max_threshold = datetime_to_ldap(datetime.now() - timedelta(days=max_age_days))
    with ldap_connection() as c:
        c.search(
            PEOPLE_OU,
            f"(&(createTimestamp<={min_threshold})(createTimestamp>={max_threshold}))",
            attributes="cn",
        )
        return [str(entry.cn) for entry in c.entries]
