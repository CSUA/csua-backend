"""
Run at project root:
python manage.py shell < apps/ldap/shell_tests/input.py > apps/ldap/shell_tests/output
"""
from apps.ldap.utils import get_user_creation_time
from apps.ldap import utils
from datetime import datetime, timezone

dt_now = datetime.now(timezone.utc)
print("Current time:", dt_now)
print("Current time LDAP:", utils.datetime_to_ldap(dt_now))
dt = datetime(2021, 2, 13, 15, 8, 37)
lt = utils.datetime_to_ldap(dt)
print("date_time_to_ldap is correct?", lt == "20210213150837Z")
print()

mem = utils.get_members_older_than()
print(len(mem), "members older than 1460 days")
mem = utils.get_members_in_age_range()
print(len(mem), "members younger than 180 days")
print()

members_0_5 = utils.get_members_in_age_range(0, 5)
print(members_0_5)
for m in members_0_5:
    print(dt_now - utils.str_to_datetime(get_user_creation_time(m)))
print()

members_0_10 = utils.get_members_in_age_range(0, 10)
print(members_0_10)
for m in members_0_10:
    print(dt_now - utils.str_to_datetime(get_user_creation_time(m)))
print()

members_5_15 = utils.get_members_in_age_range(5, 15)
print(members_5_15)
for m in members_5_15:
    print(dt_now - utils.str_to_datetime(get_user_creation_time(m)))
print()
