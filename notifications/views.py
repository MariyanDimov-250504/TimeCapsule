from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views.generic import DeleteView
from .models import Notification

class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    template_name = 'notifications/notification_confirm_delete.html'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('notifications:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Notification deleted successfully.')
        return super().delete(request, *args, **kwargs)
