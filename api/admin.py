from django.contrib import admin
from .models import User, PasswordResets, UserOnboard, UserProfile


admin.site.register(User)
admin.site.register(PasswordResets)
admin.site.register(UserOnboard)
admin.site.register(UserProfile)
    