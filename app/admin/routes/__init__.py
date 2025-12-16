"""
📂 Admin Routes Package
Import tất cả route modules để auto-register vào admin_bp
"""

# ==================== 1. AUTHENTICATION ====================
from . import auth

# ==================== 2. DASHBOARD ====================
from . import dashboard

# ==================== 3. CONTENT MANAGEMENT ====================
from . import categories
from . import products
from . import banners
from . import blogs
from . import faqs
from . import projects
from . import jobs
from . import quiz
from . import distributors
from . import popups

# ==================== 4. USER & CONTACT MANAGEMENT ====================
from . import users
from . import contacts

# ==================== 5. MEDIA & ASSETS ====================
from . import media
from . import ckeditor

# ==================== 6. SYSTEM & PERMISSIONS ====================
from . import roles
from . import features
from . import settings

# ==================== 7. WIZARDS ====================
from . import wizards


#  Export để dễ debug và kiểm tra
__all__ = [
    'auth',
    'dashboard',
    'categories',
    'products',
    'banners',
    'blogs',
    'faqs',
    'projects',
    'jobs',
    'quiz',
    'distributors',
    'popups',
    'users',
    'contacts',
    'media',
    'ckeditor',
    'roles',
    'features',
    'settings',
    'wizards',
]