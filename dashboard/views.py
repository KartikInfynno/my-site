from django.db.models.functions import TruncMonth, TruncWeek,TruncDay
from django.db.models import Count
from calendar import month
import json
from re import U
from unittest import installHandler
from urllib import response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from datetime import datetime, date
from dashboard.models import UserWaterSettings
from .serializer import (
    SetUserActivitySerializer,
    WaterSettingsSerializer,
    SetUserGoalSerializer,
    ContactUsSerializer,
    ShowAllDailyWaterGoalSerializer,
    ShowAllDailyActivitySerializer,
    UpdateDailyWaterHistorySerializor,
    UpdateDailyActivityHistorySerializor,
    ShowAcivityGraphSerializer,
    ShowDailyGoalGraphSerializer,
)
from .renderers import UserRenderer
from datetime import date
from rest_framework.permissions import IsAuthenticated
from .models import UserGoal, UserWaterSettings, UserActivity, UserGoalHistory, UserActivityHistory
from api.email import send_contact_us_success_email
from .pagintator import BasicPagination
import datetime


class WaterSettingsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            my_settings = UserWaterSettings.objects.filter(
                user_id=request.user)
            serializer = WaterSettingsSerializer(my_settings, many=True)
            return Response(serializer.data[0], status=status.HTTP_200_OK)
        else:
            return Response({'Error': "You don't Have any water settings"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user.id).exists():
            return Response({'error': 'Water Settings Already Exists'}, status=status.HTTP_200_OK)

        else:
            serializer = WaterSettingsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user_id=request.user)
                return Response({'msg': 'Settings Saved'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if UserWaterSettings.objects.filter(user_id=request.user.id).exists():
            my_settings = UserWaterSettings.objects.get(
                user_id=request.user.id)
            serializer = WaterSettingsSerializer(
                data=request.data, instance=my_settings, partial=True)
            serializer.is_valid(raise_exception=True)
            my_settings.updated_at = datetime.datetime.now()
            serializer.save(user_id=request.user)
            return Response({'msg': 'Settings Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You dont have any water settings'}, status=status.HTTP_200_OK)


class SetUserWaterGoal(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, pk=None):
        if UserGoal.objects.filter(user_id=request.user.id).exists():
            my_goal = UserGoal.objects.filter(user_id=request.user.id).last()
            serializer = SetUserGoalSerializer(my_goal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "You don't Have any water goal"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        if request.data:
            serializer = SetUserGoalSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                my_settings = UserWaterSettings.objects.get(
                    user_id=request.user)
                if serializer.validated_data['water_goal']:
                    serializer.save(user_id=request.user,
                                    water_setting=my_settings)
                    goal = int(serializer.data['water_goal'])
                    cup_size = int(my_settings.cup_size)
                    my_goal = UserGoal.objects.filter(
                        user_id=request.user.id).last()
                    my_goal.cup_count = int(goal/cup_size)
                    my_goal.start_date = date.today()
                    my_goal.save()
                    return Response({'msg': f'Goal Set Successfully '}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Please set the daily goal'}, status=status.HTTP_403_FORBIDDEN)

        else:
            return Response({'error': 'Please set the daily goal'}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk=None):
        if request.data:
            if UserGoal.objects.filter(user_id=request.user.id).exists():
                my_settings = UserWaterSettings.objects.get(
                    user_id=request.user.id)
                my_goal = UserGoal.objects.filter(
                    user_id=request.user.id).last()
                serializer = SetUserGoalSerializer(
                    data=request.data, partial=True)
                serializer2 = SetUserGoalSerializer(
                    data=request.data, instance=my_goal, partial=True)
                serializer.is_valid(raise_exception=True)
                if my_goal.start_date == date.today():
                    serializer2.is_valid(raise_exception=True)
                    serializer2.save(user_id=request.user,
                                     water_setting=my_settings)
                elif serializer.validated_data['water_goal'] == my_goal.water_goal:
                    return Response({'error': 'Updated Daily Goal Can Not Be Same As Previous Goal'})
                else:
                    my_goal.end_date = date.today()
                    my_goal.save()
                    serializer.save(
                        user_id=request.user, water_setting=my_settings, start_date=date.today())
                goal = int(serializer.validated_data['water_goal'])
                cup_size = int(my_settings.cup_size)
                my_goal = UserGoal.objects.filter(
                    user_id=request.user.id).last()
                my_goal.cup_count = int(goal/cup_size)
                my_goal.save()
                return Response({'msg': 'Goal Updated Successfully'}, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'You dont have any daily goal'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Please Insert The Daily Goal'}, status=status.HTTP_403_FORBIDDEN)


class IncreaseDrinkGlass(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, pk=None):
        if UserGoal.objects.filter(user_id=request.user.id).exists():
            my_goal = UserGoal.objects.filter(user_id=request.user.id).last()
            history = UserGoalHistory.objects.create(
                user_id=my_goal.user_id, my_goal=my_goal, date=date.today(), water_drink_time=datetime.datetime.now())
            history.save()
            return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You dont have any water goal'}, status=status.HTTP_404_NOT_FOUND)


class DecreaseDrinkGlass(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, pk=None):
        if UserGoal.objects.filter(user_id=request.user.id).exists():
            if UserGoalHistory.objects.filter(user_id=request.user.id, date=date.today()).exists():
                history = UserGoalHistory.objects.filter(
                    user_id=request.user.id).last()
                history.delete()
            else:
                return Response({'msg': "You Haven't Drunk any glass of water"}, status=status.HTTP_200_OK)
            return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You dont have any water goal'}, status=status.HTTP_404_NOT_FOUND)


class SetUserActivityGoal(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, pk=None):
        if UserActivity.objects.filter(user_id=request.user.id).exists():
            my_goal = UserActivity.objects.filter(
                user_id=request.user.id).last()
            serializer = SetUserActivitySerializer(my_goal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You Dont have any activity'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.data:
            serializer = SetUserActivitySerializer(
                data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            my_settings = UserWaterSettings.objects.get(user_id=request.user)
            serializer.save(user_id=request.user, water_setting=my_settings)
            my_activity = UserActivity.objects.filter(
                user_id=request.user).last()
            my_activity.start_date = date.today()
            my_activity.save()
            return Response({'msg': 'Activity Goal Set Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Please Enter the Activity Goal'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if request.data:
            if UserActivity.objects.filter(user_id=request.user).exists():
                my_settings = UserWaterSettings.objects.get(
                    user_id=request.user.id)
                my_goal = UserActivity.objects.filter(
                    user_id=request.user).last()
                serializer2 = SetUserActivitySerializer(
                    data=request.data, instance=my_goal, partial=True)
                serializer = SetUserActivitySerializer(
                    data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                if my_goal.start_date == date.today():
                    serializer2.is_valid(raise_exception=True)
                    serializer2.save(user_id=request.user,
                                     water_setting=my_settings)
                elif serializer.validated_data['activity_goal'] == my_goal.activity_goal:
                    return Response({'error': 'Updated Activity Goal Can Not Be Same As Previous Goal'})
                else:
                    my_goal.end_date = date.today()
                    my_goal.save()
                    serializer.save(
                        user_id=request.user, water_setting=my_settings, start_date=date.today())
                return Response({'msg': 'Settings Updated Successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You dont have any activity goal'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Please Enter the Activity Goal'}, status=status.HTTP_400_BAD_REQUEST)


class IncreaseActivityBreak(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, pk=None):
        if UserActivity.objects.filter(user_id=request.user.id).exists():
            my_goal = UserActivity.objects.filter(
                user_id=request.user.id).last()
            history = UserActivityHistory.objects.create(
                user_id=my_goal.user_id, my_activity=my_goal, date=date.today(), user_activity_time=datetime.datetime.now())
            history.save()
            return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You dont have any activity goal'}, status=status.HTTP_400_BAD_REQUEST)


class DecreaseActivityBreak(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, pk=None):
        if UserActivity.objects.filter(user_id=request.user.id).exists():
            my_goal = UserActivity.objects.filter(
                user_id=request.user.id).last()
            if UserActivityHistory.objects.filter(user_id=my_goal.user_id, date=date.today()).exists():
                history = UserActivityHistory.objects.filter(
                    user_id=my_goal.user_id, date=date.today()).last()
                history.delete()
                return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You dont have any activity'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You dont have any activity'}, status=status.HTTP_200_OK)


class ContactUsView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if request.data:
            serializer = ContactUsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                send_contact_us_success_email(serializer.data['email'])
                return Response({'msg': 'Thanks for contacting us, we will reach you soon'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Please Fill all the required fields'}, status=status.HTTP_400_BAD_REQUEST)


class ShowAllDailyWaterGoal(ListAPIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    serializer_class = ShowAllDailyWaterGoalSerializer
    pagination_class = BasicPagination

    def get_queryset(self):
        queryset = UserGoalHistory.objects.filter(user_id=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        sort_by = request.query_params.get('sort_by')
        if sort_by == 'weekly' or sort_by == 'Weekly' or sort_by == 'week' or sort_by == 'Week':
            week = date.today().strftime("%V")
            queryset = self.get_queryset().filter(date__week=week)
            cupsize = UserWaterSettings.objects.get(user_id=request.user)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserGoal.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserGoal.objects.filter(
                        user_id=request.user.id).last()
                    total_intake = UserGoalHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    today_intake = int(
                        my_goal.water_setting.cup_size) * total_intake
                    remaining_intake = int(
                        my_goal.water_goal) - int(today_intake)
                    upd = []
                    for i in serializer.data:
                        i['cup_size'] = str(cupsize.cup_size)+'ml'
                        i['goal'] = str(my_goal.water_goal)+'ml'
                        i['today_intake'] = str(today_intake)+'ml'
                        i['remaining_intake'] = str(remaining_intake)+'ml'
                        upd.append(i)
                    return self.get_paginated_response(upd)
                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': "You didnt set any water goal",
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        elif sort_by == 'monthly' or sort_by == 'Monthly' or sort_by == 'month' or sort_by == 'Month':
            month = date.today().strftime("%m")
            cupsize = UserWaterSettings.objects.get(user_id=request.user)
            queryset = self.get_queryset().filter(date__month=month)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserGoal.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserGoal.objects.filter(
                        user_id=request.user.id).last()
                    total_intake = UserGoalHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    today_intake = int(
                        my_goal.water_setting.cup_size) * total_intake
                    remaining_intake = int(
                        my_goal.water_goal) - int(today_intake)
                    upd = []
                    for i in serializer.data:
                        i['cup_size'] = str(cupsize.cup_size)+'ml'
                        i['goal'] = str(my_goal.water_goal)+'ml'
                        i['today_intake'] = str(today_intake)+'ml'
                        i['remaining_intake'] = str(remaining_intake)+'ml'
                        upd.append(i)
                    return self.get_paginated_response(upd)
                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': "You didnt set any water goal",
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        elif sort_by == 'yearly' or sort_by == 'Yearly' or sort_by == 'Yearly':
            yearly = date.today().strftime("%Y")
            cupsize = UserWaterSettings.objects.get(user_id=request.user)
            queryset = self.get_queryset().filter(date__month=yearly)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserGoal.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserGoal.objects.filter(
                        user_id=request.user.id).last()
                    total_intake = UserGoalHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    today_intake = int(
                        my_goal.water_setting.cup_size) * total_intake
                    remaining_intake = int(
                        my_goal.water_goal) - int(today_intake)
                    upd = []
                    for i in serializer.data:
                        i['cup_size'] = str(cupsize.cup_size)+'ml'
                        i['goal'] = str(my_goal.water_goal)+'ml'
                        i['today_intake'] = str(today_intake)+'ml'
                        i['remaining_intake'] = str(remaining_intake)+'ml'
                        upd.append(i)
                    return self.get_paginated_response(upd)
                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': "You didnt set any water goal",
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        else:
            queryset = self.get_queryset()
            cupsize = UserWaterSettings.objects.get(user_id=request.user)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserGoal.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserGoal.objects.filter(
                        user_id=request.user.id).last()
                    total_intake = UserGoalHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    today_intake = int(
                        my_goal.water_setting.cup_size) * total_intake
                    remaining_intake = int(
                        my_goal.water_goal) - int(today_intake)
                    upd = []
                    for i in serializer.data:
                        i['cup_size'] = str(cupsize.cup_size)+'ml'
                        i['goal'] = str(my_goal.water_goal)+'ml'
                        i['today_intake'] = str(today_intake)+'ml'
                        i['remaining_intake'] = str(remaining_intake)+'ml'
                        upd.append(i)
                    return self.get_paginated_response(upd)
                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': "You didnt set any water goal",
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })


# With Pagination
class ShowAllActivityBreak(ListAPIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    serializer_class = ShowAllDailyActivitySerializer
    pagination_class = BasicPagination

    def get_queryset(self):
        queryset = UserActivityHistory.objects.filter(
            user_id=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        sort_by = request.query_params.get('sort_by')
        if sort_by == 'weekly' or sort_by == 'Weekly' or sort_by == 'week' or sort_by == 'Week':
            week = date.today().strftime("%V")
            queryset = self.get_queryset().filter(date__week=week)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserActivity.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserActivity.objects.filter(
                        user_id=request.user.id).last()
                    total_activity = UserActivityHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    remaining_intake = int(
                        my_goal.activity_goal) - int(total_activity)
                    upd = []
                    for i in serializer.data:
                        i['goal'] = my_goal.activity_goal
                        i['today_activity'] = total_activity
                        i['remaining_intake'] = remaining_intake
                        upd.append(i)
                    return self.get_paginated_response(upd)

                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': 'You didnt set the activity goal',
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        elif sort_by == 'monthly' or sort_by == 'Monthly' or sort_by == 'month' or sort_by == 'Month':
            month = date.today().strftime("%m")
            queryset = self.get_queryset().filter(date__month=month)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserActivity.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserActivity.objects.filter(
                        user_id=request.user.id).last()
                    total_activity = UserActivityHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    remaining_intake = int(
                        my_goal.activity_goal) - int(total_activity)
                    upd = []
                    for i in serializer.data:
                        i['goal'] = my_goal.activity_goal
                        i['today_activity'] = total_activity
                        i['remaining_intake'] = remaining_intake
                        upd.append(i)
                    return self.get_paginated_response(upd)

                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': 'You didnt set the activity goal',
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        elif sort_by == 'yearly' or sort_by == 'Yearly' or sort_by == 'Yearly':
            yearly = date.today().strftime("%Y")
            queryset = self.get_queryset().filter(date__year=yearly)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserActivity.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserActivity.objects.filter(
                        user_id=request.user.id).last()
                    total_activity = UserActivityHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    remaining_intake = int(
                        my_goal.activity_goal) - int(total_activity)
                    upd = []
                    for i in serializer.data:
                        i['goal'] = my_goal.activity_goal
                        i['today_activity'] = total_activity
                        i['remaining_intake'] = remaining_intake
                        upd.append(i)
                    return self.get_paginated_response(upd)

                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': 'You didnt set the activity goal',
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })

        else:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                if UserActivity.objects.filter(user_id=request.user.id).exists():
                    my_goal = UserActivity.objects.filter(
                        user_id=request.user.id).last()
                    total_activity = UserActivityHistory.objects.filter(
                        user_id=request.user.id, date=date.today()).count()
                    remaining_intake = int(
                        my_goal.activity_goal) - int(total_activity)
                    upd = []
                    for i in serializer.data:
                        i['goal'] = my_goal.activity_goal
                        i['today_activity'] = total_activity
                        i['remaining_intake'] = remaining_intake
                        upd.append(i)
                    return self.get_paginated_response(upd)

                else:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': 'You didnt set the activity goal',
                    })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': status.HTTP_200_OK,
                'data': upd,
            })


class DailyGoalAchievement(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        goal = {}
        if UserGoalHistory.objects.filter(user_id=request.user).exists():
            water = UserGoalHistory.objects.filter(
                user_id=request.user, date=date.today()).count()
            goal["todays_water"] = water
            if UserGoalHistory.objects.filter(user_id=request.user).exists():
                activity = UserActivityHistory.objects.filter(
                    user_id=request.user, date=date.today()).count()
                goal["todays_activity"] = activity
            else:
                goal["todays_activity"] = None
        else:
            goal["todays_water"] = None
        return Response(goal, status=status.HTTP_200_OK)


class ActivityBreakStats(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                date = datetime.datetime.today()
                today = datetime.date.today()
                week = date.strftime("%V")
                month = date.strftime("%m")
                today_total_activity = UserActivityHistory.objects.filter(
                    date=today, user_id=request.user.id).count()
                week_total_activity = UserActivityHistory.objects.filter(
                    date__week=week, user_id=request.user.id).count()
                month_total_activity = UserActivityHistory.objects.filter(
                    date__month=month, user_id=request.user.id).count()
                print(week_total_activity, today_total_activity, month_total_activity)

                return Response({'Today': today_total_activity,
                                'This Week': week_total_activity,
                                'This Month': month_total_activity}, status=status.HTTP_200_OK)
            else:
                return Response({'error':'You didnt set any activity goal'})
        else:
            return Response({'error':'You didnt set your water and activity settings'})

class WaterIntakeStats(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                date = datetime.datetime.today()
                today = datetime.date.today()
                week = date.strftime("%V")
                month = date.strftime("%m")
                water_setting = UserWaterSettings.objects.get(user_id=request.user)
                today_total_cups = UserGoalHistory.objects.filter(
                    date=today, user_id=request.user.id).count()
                week_total_cups = UserGoalHistory.objects.filter(
                    date__week=week, user_id=request.user.id).count()
                month_total_cups = UserGoalHistory.objects.filter(
                    date__month=month, user_id=request.user.id).count()
                print(week_total_cups, today_total_cups, month_total_cups)
                cup_size = int(water_setting.cup_size)
                today_drunk = cup_size*today_total_cups
                week_drunk = cup_size*week_total_cups
                month_drunk = cup_size*month_total_cups

                return Response({'Today': today_drunk,
                                'This Week': week_drunk,
                                'This Month': month_drunk}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You didnt set any daily goal'})

        else:
            return Response({'error': 'You didnt set any water settings'})


class UpdateWaterGoalHistory(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                data_id = request.query_params.get('id')
                if data_id:
                    if UserGoalHistory.objects.filter(id=data_id).exists():
                        print("abc")
                        data = UserGoalHistory.objects.get(id=data_id)
                        serializer = UpdateDailyWaterHistorySerializor(
                            data=request.data, instance=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(user_id=request.user)
                        return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Data not found'})
                else:
                    return Response({'error': 'Something went wrong try again'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})

    def delete(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                data_id = request.query_params.get('id')
                if data_id:
                    if UserGoalHistory.objects.filter(id=data_id).exists():
                        data = UserGoalHistory.objects.get(id=data_id)
                        data.delete()
                        return Response({'msg': 'Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({'error': 'Data not found'})
                else:
                    return Response({'msg': 'Something went wrong try again'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})


class UpdateActivityGoalHistory(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                data_id = request.query_params.get('id')
                if data_id:
                    if UserActivityHistory.objects.filter(id=data_id).exists():
                        data = UserActivityHistory.objects.get(id=data_id)
                        serializer = UpdateDailyActivityHistorySerializor(
                            data=request.data, instance=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(user_id=request.user)
                        return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Data not found'})
                else:
                    return Response({'error': 'Something went wrong try again'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})

    def delete(self, request, format=None):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                data_id = request.query_params.get('id')
                if data_id:
                    if UserActivityHistory.objects.filter(id=data_id).exists():
                        data = UserActivityHistory.objects.get(id=data_id)
                        data.delete()
                        return Response({'msg': 'Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({'error': 'Data not found'})
                else:
                    return Response({'error': 'Something went wrong try again'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})

def ExtractMonth(date):
    datem = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datem.month


class ShowYearlyWaterStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                if UserGoalHistory.objects.filter(user_id=request.user).exists():
                    month_data = UserGoalHistory.objects.annotate(month=TruncMonth('date')).values(
                        'month').annotate(Count=Count('id')).values('month', 'Count')
                    li = []
                    for i in month_data:
                        i['month'] = i['month'].strftime("%B")
                        li.append(i)
                    return Response({'data': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any goal history'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})


class ShowYearlyActivityStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                if UserActivityHistory.objects.filter(user_id=request.user).exists():
                    date = datetime.datetime.today()
                    month_data = UserActivityHistory.objects.annotate(month=TruncMonth(
                        'date')).values('month').annotate(Count=Count('id')).values('month', 'Count')
                    li = []
                    for i in month_data:
                        i['month'] = i['month'].strftime("%B")
                        li.append(i)
                    return Response({'msg': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any activity goal history'})
            else:
                return Response({'error': 'You didnt set any Activity Goal'})
        else:
            return Response({'error': 'You didnt set any activity settings'})



class ShowMonthlyWaterGoalStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                if UserGoalHistory.objects.filter(user_id=request.user).exists():
                    month_data = UserGoalHistory.objects.annotate(week=TruncWeek(
                        'date')).values('week').annotate(Count=Count('id')).values('week', 'Count')
                    li = []
                    for i in month_data:
                        i['week'] = i['week'].strftime("%m/%d/%Y")
                        li.append(i)
                    return Response({'msg': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any goal history'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})

class ShowMonthlyActivityStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                if UserActivityHistory.objects.filter(user_id=request.user).exists():
                    month_data = UserActivityHistory.objects.annotate(week=TruncWeek(
                        'date')).values('week').annotate(Count=Count('id')).values('week', 'Count')
                    li = []
                    for i in month_data:
                        i['week'] = i['week'].strftime("%m/%d/%Y")
                        li.append(i)
                    return Response({'msg': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any activity goal history'})
            else:
                return Response({'error': 'You didnt set any Activity Goal'})
        else:
            return Response({'error': 'You didnt set any activity settings'})


class ShowWeeklyWaterGoalStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                if UserGoalHistory.objects.filter(user_id=request.user).exists():
                    month_data = UserGoalHistory.objects.annotate(day=TruncDay(
                        'date')).values('day').annotate(Count=Count('id')).values('day', 'Count')
                    li = []
                    for i in month_data:
                        i['day'] = i['day'].strftime("%m/%d/%Y")
                        li.append(i)
                    return Response({'msg': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any goal history'})
            else:
                return Response({'error': 'You didnt set any daily goal'})
        else:
            return Response({'error': 'You didnt set any water settings'})


class ShowWeeklyActivityStatistics(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                if UserActivityHistory.objects.filter(user_id=request.user).exists():
                    month_data = UserActivityHistory.objects.annotate(day=TruncDay(
                        'date')).values('day').annotate(Count=Count('id')).values('day', 'Count')
                    li = []
                    for i in month_data:
                        i['day'] = i['day'].strftime("%m/%d/%Y")
                        li.append(i)
                    return Response({'msg': li}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You dont have any activity goal history'})
            else:
                return Response({'error': 'You didnt set any Activity Goal'})
        else:
            return Response({'error': 'You didnt set any activity settings'})

class ShowActivityByDate(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserActivity.objects.filter(user_id=request.user).exists():
                if UserActivityHistory.objects.filter(user_id=request.user).exists():
                    date = request.query_params.get('date')
                    if date:
                        data = UserActivityHistory.objects.filter(
                            user_id=request.user, date=date)
                        print(data)
                        serializer = ShowAllDailyActivitySerializer(data=data, many=True)
                        serializer.is_valid()
                        return Response({'total_activity': data.count(), 'data': serializer.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Something went wrong try again'})
                else:
                    return Response({'error': 'You dont have any activity goal history'})
            else:
                return Response({'error': 'You didnt set any Activity Goal'})
        else:
            return Response({'error': 'You didnt set any activity settings'})

class ShowWaterGoalByDate(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if UserWaterSettings.objects.filter(user_id=request.user).exists():
            if UserGoal.objects.filter(user_id=request.user).exists():
                if UserGoalHistory.objects.filter(user_id=request.user).exists():
                    date = request.query_params.get('date')
                    if date:
                        data = UserGoalHistory.objects.filter(
                            user_id=request.user, date=date)
                        print(data)
                        serializer = ShowAllDailyWaterGoalSerializer(data=data, many=True)
                        serializer.is_valid()
                        return Response({'total_intake': data.count(), 'data': serializer.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Something went wrong try again'})
                else:
                    return Response({'error': 'You dont have any water goal history'})
            else:
                return Response({'error': 'You didnt set any water Goal'})
        else:
            return Response({'error': 'You didnt set any Water goal settings'})
