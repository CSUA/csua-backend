from django.contrib import admin

from .models import User, Computer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    pass
