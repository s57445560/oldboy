from django.contrib import admin

from class_app import models
# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_type',)


class registerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username','password','make_time','change_time',)


class CampusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

admin.site.register(models.User_type,ArticleAdmin)
admin.site.register(models.UserInfo,registerAdmin)
admin.site.register(models.Campus,CampusAdmin)

admin.site.register(models.Course)
