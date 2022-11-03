from django.contrib import admin
from .models import ContactUs, Notification, UserActivityHistory, UserGoalHistory,UserWaterSettings,UserGoal,UserActivity

admin.site.register(UserWaterSettings)
admin.site.register(UserGoalHistory)
admin.site.register(ContactUs)
admin.site.register(UserActivityHistory)
admin.site.register(UserActivity)
admin.site.register(UserGoal)
admin.site.register(Notification)
