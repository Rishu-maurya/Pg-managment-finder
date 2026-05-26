from django.contrib import admin
from django.utils.html import format_html
from .models import MyUser, Notification


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_owner', )
    readonly_fields = ('image_tag',)
    search_fields = ('email', 'username')
    list_filter = ('is_owner', 'is_admin', 'is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'date_of_birth', 'phone', 'profile_image','image_tag', 'is_owner', 'aadhar_card', 'address', 'city', 'state', 'pin_code', 'is_admin', 'is_staff', 'is_active', 'is_superadmin')}),

    )


    def image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.profile_image.url)
        return "-"
    image_tag.short_description = 'Profile Image'

admin.site.register(MyUser, MyUserAdmin)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'notification_type')
        return self.readonly_fields
