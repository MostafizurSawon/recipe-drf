from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name', 'image']
    
    def first_name(self,obj):
        return obj.user.first_name
    
    def last_name(self,obj):
        return obj.user.last_name

admin.site.register(models.User)
admin.site.register(models.UserProfile, UserAdmin)
