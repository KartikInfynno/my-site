from django.urls import path
from . import views

urlpatterns = [
    path('contact-us/', views.ContactUsView.as_view()),
    path('water/settings/', views.WaterSettingsView.as_view()),
    path('daily/goal/', views.SetUserWaterGoal.as_view()),
    path('activity/goal/', views.SetUserActivityGoal.as_view()),
    path('increase/glass/count/', views.IncreaseDrinkGlass.as_view()),
    path('decrease/glass/count/', views.DecreaseDrinkGlass.as_view()),
    path('increase/activity/break/', views.IncreaseActivityBreak.as_view()),
    path('decrease/activity/break/', views.DecreaseActivityBreak.as_view()),
    path('water/goal/history/', views.ShowAllDailyWaterGoal.as_view()),
    path('activity/goal/history/', views.ShowAllActivityBreak.as_view()),
    path('daily/goal/achievement/', views.DailyGoalAchievement.as_view()),
    path('water/intake/stats/', views.WaterIntakeStats.as_view()),
    path('activity/break/stats/', views.ActivityBreakStats.as_view()),
    path('update/water/history/', views.UpdateWaterGoalHistory.as_view()),
    path('update/activity/history/', views.UpdateActivityGoalHistory.as_view()),
    path('water/weekly-statistics/', views.ShowWeeklyWaterGoalStatistics.as_view()),
    path('water/yearly-statistics/', views.ShowYearlyWaterStatistics.as_view()),
    path('water/monthly-statistics/', views.ShowMonthlyWaterGoalStatistics.as_view()),
    path('activity/weekly-statistics/', views.ShowWeeklyActivityStatistics.as_view()),
    path('activity/monthly-statistics/', views.ShowMonthlyActivityStatistics.as_view()),
    path('activity/yearly-statistics/', views.ShowYearlyActivityStatistics.as_view()),
]
