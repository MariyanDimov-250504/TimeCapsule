from django import forms
from django.core.exceptions import ValidationError
from .models import Capsule, CapsuleContent
from datetime import date


class CapsuleForm(forms.ModelForm):
    class Meta:
        model = Capsule
        fields = ['title', 'description', 'open_date', 'privacy', 'allowed_users', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for your capsule'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what memories you are preserving...'
            }),
            'open_date': forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
            }),
            'privacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'allowed_users': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        help_texts = {
            'open_date': 'Choose a future date when this capsule can be opened.',
            'privacy': 'Who can see this capsule?',
            'allowed_users': 'Hold Ctrl/Cmd to select multiple users (only for Shared privacy)',
        }

    def clean_open_date(self):
        open_date = self.cleaned_data.get('open_date')
        from django.utils import timezone
        if open_date and open_date <= timezone.now():
            raise ValidationError('Open date and time must be in the future.')
        return open_date

    def clean(self):
        cleaned_data = super().clean()
        privacy = cleaned_data.get('privacy')
        allowed_users = cleaned_data.get('allowed_users')

        if privacy == 'shared' and not allowed_users:
            self.add_error('allowed_users', 'You must select at least one user for shared capsules.')

        return cleaned_data


class CapsuleContentForm(forms.ModelForm):
    class Meta:
        model = CapsuleContent
        fields = ['content_type', 'title', 'text_content', 'image']
        widgets = {
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional title'}),
            'text_content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message or memory here...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        text_content = cleaned_data.get('text_content')
        image = cleaned_data.get('image')

        if content_type == 'text' and not text_content:
            self.add_error('text_content', 'Please enter a text message.')

        if content_type == 'image' and not image:
            self.add_error('image', 'Please upload an image.')

        return cleaned_data
