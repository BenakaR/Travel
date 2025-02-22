from django.contrib import admin
from .models import User, Chat

class UserAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'route', 'stops', 'distance')
    search_fields = ('session_id',)

class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'created_at', 'message', 'type')

admin.site.register(User, UserAdmin)
admin.site.register(Chat, ChatAdmin)