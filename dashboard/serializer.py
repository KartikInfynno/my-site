from dataclasses import field
from .models import ContactUs,UserGoal,UserWaterSettings,UserActivity,UserGoalHistory,UserActivityHistory
from rest_framework import serializers


class WaterSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserWaterSettings
        exclude = ['user_id', 'created_at', 'updated_at']

class SetUserGoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGoal
        exclude = ['user_id', 'start_date', 'water_setting','end_date']

class SetUserActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivity
        exclude = ['user_id', 'start_date', 'water_setting']

class CountDrunkWaterGlassSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = ['current_cup_count']

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'

class ListUserGoalsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGoal
        exclude = ['user_id','water_setting']

class ShowAllDailyWaterGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoalHistory
        fields = ['id','date','water_drink_time']


class ShowAllDailyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityHistory
        fields = ['id','date','user_activity_time']

class UpdateDailyWaterHistorySerializor(serializers.ModelSerializer):
    class Meta:
        model = UserGoalHistory
        fields = ['date','water_drink_time']

class UpdateDailyActivityHistorySerializor(serializers.ModelSerializer):
    class Meta:
        model = UserActivityHistory
        fields = ['date','user_activity_time']

class ShowDailyGoalGraphSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGoalHistory
        fields = ['date']

class ShowAcivityGraphSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivityHistory
        fields = ['date']
