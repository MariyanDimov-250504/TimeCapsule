from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.views.generic import DeleteView
from .models import Notification

class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    template_name = 'notifications/notification_confirm_delete.html'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('notifications:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.user.notifications.filter(is_read=False).update(is_read=True)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Notification deleted successfully.')
        return super().delete(request, *args, **kwargs)

class NotificationMarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        return redirect(notification.link or reverse('notifications:list'))
