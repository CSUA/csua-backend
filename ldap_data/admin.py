from django.contrib import admin
from . import models

@admin.register(models.LdapGroup)
class LDAPGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']
    list_display = ['gid', 'name']
