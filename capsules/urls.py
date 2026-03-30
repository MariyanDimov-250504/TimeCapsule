from django.urls import path
from . import views

app_name = 'capsules'

urlpatterns = [
    path('my/', views.MyCapsulesView.as_view(), name='my_capsules'),
    path('public/', views.PublicCapsulesView.as_view(), name='public'),
    path('create/', views.CapsuleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CapsuleDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.CapsuleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.CapsuleDeleteView.as_view(), name='delete'),
    path('<int:pk>/add-content/', views.AddContentView.as_view(), name='add_content'),
]

