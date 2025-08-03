from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Job, JobTask, Equipment

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'status', 'priority', 'scheduled_date', 'overdue', 'created_by', 'assigned_to')
    list_filter = ('status', 'priority', 'overdue')
    search_fields = ('title', 'client_name')
    ordering = ('-scheduled_date',)

class JobTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'job', 'status', 'order', 'completed_at')
    list_filter = ('status', 'job')
    search_fields = ('title', 'job__title')
    ordering = ('job', 'order')
    filter_horizontal = ('required_equipment',)

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'serial_number', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'serial_number')
    ordering = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobTask, JobTaskAdmin)
admin.site.register(Equipment, EquipmentAdmin)