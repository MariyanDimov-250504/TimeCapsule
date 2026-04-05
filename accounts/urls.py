from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]

