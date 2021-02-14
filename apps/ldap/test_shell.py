from apps.ldap import utils
from datetime import datetime

dt = datetime(2021, 2, 13, 15, 8, 37)
lt = utils.datetime_to_ldap(dt)
print("lt matches:", lt == "20210213150837Z")
mem = utils.get_new_members()
print("New members last 180 days:", len(mem))
print(utils.get_new_members(10))
print(utils.get_new_members(5))
print(utils.get_new_members(2))
print(utils.get_new_members(0))
