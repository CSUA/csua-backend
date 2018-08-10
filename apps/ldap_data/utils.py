from .models import LdapUser


def uname_to_realname(uname):
    try:
        user = LdapUser.objects.get(username=uname)
    except LdapUser.DoesNotExist:
        return "Phillip E. Nunez"
    print(user.gecos.split(","))
    return user.gecos.split(",", 1)[0]
