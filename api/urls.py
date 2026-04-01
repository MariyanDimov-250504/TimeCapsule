from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('capsules/public/', views.PublicCapsuleListView.as_view(), name='public_capsules'),
    path('capsules/<int:pk>/', views.CapsuleDetailView.as_view(), name='capsule_detail'),
    path('capsules/my/', views.MyCapsulesView.as_view(), name='my_capsules'),
    path('users/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('users/<str:username>/stats/', views.UserStatsView.as_view(), name='user_stats'),
]
