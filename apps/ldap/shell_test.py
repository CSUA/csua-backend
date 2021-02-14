"""
Run at project root:
python manage.py shell < apps/ldap/shell_test.py
"""
from apps.ldap import utils
from datetime import datetime

dt = datetime(2021, 2, 13, 15, 8, 37)
lt = utils.datetime_to_ldap(dt)
print("lt matches:", lt == "20210213150837Z")
mem = utils.get_members_older()
print(len(mem), "members older than 1460 days")
mem = utils.get_members_age_range()
print(len(mem), "members younger than 180 days")
print(utils.get_members_age_range(0, 5))
print(utils.get_members_age_range(0, 10))
print(utils.get_members_age_range(5, 15))
