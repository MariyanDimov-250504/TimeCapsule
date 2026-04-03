from django.contrib import admin
from .models import Capsule, CapsuleContent, Report

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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['capsule', 'reported_by', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason']
    actions = ['mark_reviewed', 'mark_action_taken']

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')

    mark_reviewed.short_description = "Mark as reviewed"

    def mark_action_taken(self, request, queryset):
        queryset.update(status='action_taken')

    mark_action_taken.short_description = "Mark action taken"
