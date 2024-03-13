from django.contrib import admin

from users.models import CustomUser,Story,UserStory

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Story)
admin.site.register(UserStory)
