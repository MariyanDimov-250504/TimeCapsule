from django.contrib import admin
from .models import Capsule, CapsuleContent

class CapsuleContentInline(admin.TabularInline):
    model = CapsuleContent
    extra = 1

@admin.register(Capsule)
class CapsuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'open_date', 'status', 'privacy', 'views_count']
    list_filter = ['status', 'privacy', 'created_at']
    search_fields = ['title', 'creator__username']
    inlines = [CapsuleContentInline]
    readonly_fields = ['opened_at', 'views_count']

@admin.register(CapsuleContent)
class CapsuleContentAdmin(admin.ModelAdmin):
    list_display = ['capsule', 'content_type', 'title', 'created_at']
    list_filter = ['content_type']

