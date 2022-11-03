from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from api.models import User


water_unit = (
    ('ml', 'ml'),
    ('l', 'l'),
)

cup_size = (
    ('100', 100),
    ('150', 150),
    ('200', 200),
    ('250', 250),
    ('300', 300),
)


class UserWaterSettings(models.Model):

    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    water_unit = models.CharField(
        max_length=5, choices=water_unit, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    cup_size = models.CharField(
        max_length=10, choices=cup_size, blank=True, null=True)
    # hourly_reminder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user_id.email


class UserGoal(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    water_setting = models.ForeignKey(
        UserWaterSettings, on_delete=models.CASCADE)
    water_goal = models.CharField(max_length=5, blank=True, null=True)
    cup_count = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.user_id.email

class UserGoalHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    my_goal  = models.ForeignKey(UserGoal, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    water_drink_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.user_id.email


class UserActivity(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    water_setting = models.ForeignKey(
        UserWaterSettings, on_delete=models.CASCADE)
    activity_goal = models.CharField(max_length=5, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user_id.email}'

class UserActivityHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    my_activity = models.ForeignKey(UserActivity, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    user_activity_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.my_activity}  {self.my_activity.id}'

class ContactUs(models.Model):
    first_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    message = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

notification_type = (
    ('activity', 'activity'),
    ('water', 'water')
)
class Notification(models.Model):
    type = models.CharField(choices= notification_type, max_length=10)
    message = models.TextField(max_length=255, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def save(self,*args, **kwargs):
        channel_layer = get_channel_layer()
        # notification_obj = Notification.objects.filter(user=self.request.user.id)
        data = {
            # 'count': notification_obj,
            'current_notification': self.message,
            'notification_type': self.type,
        }
        async_to_sync(channel_layer.group_send)(
            'notification_broadcast', {
                'type' : 'send_notification',
                'value' : data
            }
        )
        super(Notification, self).save(*args, **kwargs)
