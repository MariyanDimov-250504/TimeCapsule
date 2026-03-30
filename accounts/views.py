from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.username}! Your account has been created successfully.')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})

