from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from base import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
    path('item_details/<int:item_id>/', views.item_detail, name='item_detail'),
    path('post/', views.post, name='post'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/user/create/', views.admin_create_user, name='admin_create_user'),
    path('dashboard/user/bulk-create/', views.admin_bulk_create_users, name='admin_bulk_create_users'),
    path('dashboard/user/download-sample/', views.download_sample_excel, name='download_sample_excel'),
    path('dashboard/user/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/item/<int:item_id>/delete/', views.admin_delete_item, name='admin_delete_item'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/user/<int:user_id>/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('privacy/', views.privacy, name='privacy'),
    path('api/recent-items/', views.api_recent_items, name='api_recent_items'),
    path('api/stats/', views.api_stats, name='api_stats'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': getattr(settings, 'MEDIA_ROOT', settings.BASE_DIR / 'media')}),
]

