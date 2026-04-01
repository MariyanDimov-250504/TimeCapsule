from django.urls import path
from django.views.generic import ListView
from .models import Notification
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
]
