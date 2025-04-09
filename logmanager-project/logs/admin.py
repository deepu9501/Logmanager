from django.contrib import admin
from .models import LogSource, LogEntry

@admin.register(LogSource)
class LogSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'description', 'created_at', 'updated_at')
    list_filter = ('type', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'type')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'source', 'severity', 'category', 'event_id', 'is_read', 'is_flagged')
    list_filter = ('severity', 'source', 'is_read', 'is_flagged', 'timestamp')
    search_fields = ('message', 'category', 'event_id', 'source__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    actions = ['mark_as_read', 'mark_as_unread', 'flag', 'unflag']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected logs as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected logs as unread"

    def flag(self, request, queryset):
        queryset.update(is_flagged=True)
    flag.short_description = "Flag selected logs"

    def unflag(self, request, queryset):
        queryset.update(is_flagged=False)
    unflag.short_description = "Unflag selected logs" 