from django.contrib import admin
from .models import Company, ChatHistory

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'sector', 'description']
    search_fields = ['name', 'sector']
    list_filter = ['sector']

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user_message', 'bot_response', 'session_id']
    list_filter = ['timestamp']
    search_fields = ['user_message', 'bot_response', 'session_id']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-timestamp')
