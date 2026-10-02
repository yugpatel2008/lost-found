"""
Re-export views from base.views for backwards compatibility.
All domain business logic and view controllers reside in base/views.py and base/utils.py.
"""
from base.views import (
    home,
    browse,
    item_detail,
    post,
    privacy,
    login,
    logout,
    change_password,
    dashboard,
    admin_create_user,
    admin_bulk_create_users,
    admin_delete_user,
    admin_delete_item,
    admin_reset_password,
    download_sample_excel,
    api_recent_items,
    api_stats,
)
