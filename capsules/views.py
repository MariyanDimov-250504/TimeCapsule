from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import models
from .models import Capsule, CapsuleContent, Report
from .forms import CapsuleForm, CapsuleContentForm

class PublicCapsulesView(ListView):
    model = Capsule
    template_name = 'capsules/capsule_list.html'
    context_object_name = 'capsules'
    paginate_by = 6

    def get_queryset(self):
        return Capsule.objects.filter(privacy='public', status='sealed')

class MyCapsulesView(LoginRequiredMixin, ListView):
    model = Capsule
    template_name = 'capsules/my_capsules.html'
    context_object_name = 'capsules'
    paginate_by = 6

    def get_queryset(self):
        queryset = Capsule.objects.filter(creator=self.request.user)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        privacy_filter = self.request.GET.get('privacy')
        if privacy_filter and privacy_filter in ['public', 'shared', 'private']:
            queryset = queryset.filter(privacy=privacy_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['privacy_filter'] = self.request.GET.get('privacy', '')
        return context


class CapsuleDetailView(DetailView):
    model = Capsule
    template_name = 'capsules/capsule_detail.html'
    context_object_name = 'capsule'

    def dispatch(self, request, *args, **kwargs):
        capsule = self.get_object()
        if not capsule.can_user_view(request.user):
            messages.error(request, 'You do not have permission to view this capsule.')
            return redirect('home')
        cookie_name = f'viewed_capsule_{capsule.id}'
        if not request.COOKIES.get(cookie_name):
            capsule.views_count += 1
            capsule.save(update_fields=['views_count'])

        response = super().dispatch(request, *args, **kwargs)

        if not request.COOKIES.get(cookie_name):
            response.set_cookie(cookie_name, 'true', max_age=30 * 24 * 60 * 60)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capsule = self.get_object()
        context['can_open'] = capsule.can_user_open(self.request.user)
        context['contents'] = capsule.contents.all()
        context['now'] = timezone.now()
        return context


class CapsuleCreateView(LoginRequiredMixin, CreateView):
    model = Capsule
    form_class = CapsuleForm
    template_name = 'capsules/capsule_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['allowed_users'].queryset = self.request.user.__class__.objects.exclude(
            id=self.request.user.id
        ).exclude(
            is_staff=True
        ).exclude(
            is_superuser=True
        )
        return form

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, f'Your capsule "{form.instance.title}" has been created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('capsules:my_capsules')


class CapsuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Capsule
    form_class = CapsuleForm
    template_name = 'capsules/capsule_form.html'

    def test_func(self):
        capsule = self.get_object()
        return self.request.user == capsule.creator

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['allowed_users'].queryset = self.request.user.__class__.objects.exclude(
            id=self.request.user.id
        ).exclude(
            is_staff=True
        ).exclude(
            is_superuser=True
        )
        return form

    def form_valid(self, form):
        messages.success(self.request, f'Capsule "{form.instance.title}" has been updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('capsules:my_capsules')


class CapsuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Capsule
    template_name = 'capsules/capsule_confirm_delete.html'
    success_url = reverse_lazy('capsules:my_capsules')

    def test_func(self):
        capsule = self.get_object()
        return self.request.user == capsule.creator

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Capsule has been deleted.')
        return super().delete(request, *args, **kwargs)


class AddContentView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CapsuleContent
    form_class = CapsuleContentForm
    template_name = 'capsules/add_content.html'

    def dispatch(self, request, *args, **kwargs):
        self.capsule = get_object_or_404(Capsule, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user == self.capsule.creator and self.capsule.status == 'sealed'

    def form_valid(self, form):
        form.instance.capsule = self.capsule
        messages.success(self.request, 'Content added to your capsule!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('capsules:detail', kwargs={'pk': self.capsule.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['capsule'] = self.capsule
        return context


class ReportCapsuleView(LoginRequiredMixin, CreateView):
    model = Report
    fields = ['reason', 'description']
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        self.capsule = get_object_or_404(Capsule, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        existing_report = Report.objects.filter(
            capsule=self.capsule,
            reported_by=self.request.user
        ).exists()
        if existing_report:
            messages.warning(self.request, 'You have already reported this capsule.')
            return redirect('capsules:detail', pk=self.capsule.pk)

        form.instance.capsule = self.capsule
        form.instance.reported_by = self.request.user
        form.save()

        messages.success(self.request, 'Report submitted. Thank you for helping keep our community safe!')
        return redirect('capsules:detail', pk=self.capsule.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error submitting your report. Please try again.')
        return redirect('capsules:detail', pk=self.capsule.pk)
