"""
📦 Admin Blueprint Package
Quản lý toàn bộ admin panel với RBAC
"""

from flask import Blueprint

# Tạo Blueprint chính
admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

# Import routes SAU KHI tạo blueprint (tránh circular import)
from app.admin.routes import (
    auth,
    dashboard,
    categories,
    products,
    banners,
    blogs,
    faqs,
    projects,
    jobs,
    quiz,
    distributors,
    popups,
    users,
    contacts,
    media,
    ckeditor,
    roles,
    features,
    settings,
)


# Export để dễ import từ nơi khác
__all__ = ['admin_bp']