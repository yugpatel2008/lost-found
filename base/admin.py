from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Item, UserProfile, DEPARTMENT_CHOICES


# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_user_role(user):
    """Return the role of a staff user from their profile."""
    try:
        return user.profile.role
    except Exception:
        return None


def get_user_dept(user):
    """Return the department of a staff user."""
    try:
        return user.profile.department
    except Exception:
        return None


# ─── UserProfile Inline ───────────────────────────────────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Role & Department'
    fields = ('role', 'department')
    extra = 0


# ─── Custom User Admin ────────────────────────────────────────────────────────
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display  = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_dept', 'is_staff')
    list_filter   = ('is_staff', 'is_active', 'profile__role', 'profile__department')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    @admin.display(description='Role')
    def get_role(self, obj):
        try:
            r = obj.profile.role
            colors = {'principal': '#1a56db', 'hod': '#16a34a', 'student': '#6b7280'}
            return format_html(
                '<span style="color:{}; font-weight:bold;">{}</span>',
                colors.get(r, '#000'),
                obj.profile.get_role_display()
            )
        except Exception:
            return '—'

    @admin.display(description='Department')
    def get_dept(self, obj):
        try:
            return obj.profile.department or '—'
        except Exception:
            return '—'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        role = get_user_role(request.user)
        dept = get_user_dept(request.user)
        if role == 'principal':
            return qs  # Principal sees all users
        if role == 'hod' and dept:
            # HOD sees only users from their department
            return qs.filter(profile__department=dept)
        return qs.none()

    def has_module_perms(self, request, app_label=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        role = get_user_role(request.user)
        if role in ('principal', 'hod'):
            if obj is None:
                return True
            # HOD cannot change principal or superusers
            if obj.is_superuser:
                return False
            try:
                obj_role = obj.profile.role
                if role == 'hod' and obj_role in ('principal', 'hod'):
                    return False
            except Exception:
                pass
            return True
        return False

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        role = get_user_role(request.user)
        if role == 'principal':
            if obj and obj.is_superuser:
                return False
            return True
        return False  # HOD cannot delete users


# ─── Item Admin ───────────────────────────────────────────────────────────────
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ('name', 'item_type_badge', 'location_found', 'date_found',
                     'contact_info', 'posted_by', 'created_at')
    list_filter   = ('item_type', 'location_found', 'date_found')
    search_fields = ('name', 'description', 'tags', 'contact_info')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Item Info', {
            'fields': ('item_type', 'name', 'description', 'file', 'tags')
        }),
        ('Location & Date', {
            'fields': ('location_found', 'date_found')
        }),
        ('Meetup Details (for Found items)', {
            'fields': ('meetup_place', 'meetup_date', 'meetup_time'),
            'classes': ('collapse',),
        }),
        ('Contact & Meta', {
            'fields': ('contact_info', 'posted_by', 'created_at')
        }),
    )

    @admin.display(description='Type')
    def item_type_badge(self, obj):
        if obj.item_type == 'lost':
            return format_html('<span style="background:#fef9c3;color:#92400e;padding:2px 8px;border-radius:99px;font-weight:bold;font-size:11px;">LOST</span>')
        elif obj.item_type == 'found':
            return format_html('<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:99px;font-weight:bold;font-size:11px;">FOUND</span>')
        return obj.item_type or '—'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        role = get_user_role(request.user)
        dept = get_user_dept(request.user)
        if role == 'principal':
            return qs  # See all
        if role == 'hod' and dept:
            # HOD sees items only from their department location
            return qs.filter(location_found=dept)
        return qs.none()

    def has_module_perms(self, request, app_label=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


# ─── UserProfile Admin (standalone for superuser) ────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'role', 'department')
    list_filter   = ('role', 'department')
    search_fields = ('user__username', 'user__email', 'user__first_name')

    def has_module_perms(self, request, app_label=None):
        return request.user.is_superuser  # Only superuser sees this directly


# ─── Re-register User with custom admin ──────────────────────────────────────
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ─── Admin Site Branding ──────────────────────────────────────────────────────
admin.site.site_header  = 'Indus Uni. Lost & Found — Admin'
admin.site.site_title   = 'Lost & Found Admin'
admin.site.index_title  = 'Management Panel'