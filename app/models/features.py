"""
Feature Flags System - Hệ thống bật/tắt chức năng
Quản lý các module có thể enable/disable mà không cần xóa code
"""
from app.models.settings import get_setting, set_setting
from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

# ==================== DANH SÁCH FEATURES CÓ THỂ BẬT/TẮT ====================
AVAILABLE_FEATURES = {
    'blogs': {
        'name': 'Tin tức / Blog',
        'description': 'Quản lý tin tức, bài viết blog',
        'icon': 'bi-newspaper',
        'admin_routes': ['admin.blogs', 'admin.add_blog', 'admin.edit_blog', 'admin.delete_blog'],
        'main_routes': ['main.blog', 'main.blog_detail'],
        'menu_group': 'content'
    },
    'products': {
        'name': 'Sản phẩm',
        'description': 'Quản lý danh mục và sản phẩm',
        'icon': 'bi-box-seam',
        'admin_routes': ['admin.products', 'admin.product_create', 'admin.product_edit', 'admin.product_delete',
                         'admin.categories', 'admin.category_create', 'admin.category_edit', 'admin.category_delete'],
        'main_routes': ['main.products', 'main.product_detail'],
        'menu_group': 'content'
    },
    'projects': {
        'name': 'Dự án',
        'description': 'Quản lý các dự án đã thực hiện',
        'icon': 'bi-building',
        'admin_routes': ['admin.projects', 'admin.project_create', 'admin.project_edit', 'admin.project_delete'],
        'main_routes': ['main.projects', 'main.project_detail'],
        'menu_group': 'content'
    },
    'careers': {
        'name': 'Tuyển dụng',
        'description': 'Quản lý tin tuyển dụng',
        'icon': 'bi-briefcase',
        'admin_routes': ['admin.jobs', 'admin.job_create', 'admin.job_edit', 'admin.job_delete'],
        'main_routes': ['main.careers', 'main.job_detail'],
        'menu_group': 'content'
    },
    'quiz': {
        'name': 'Trắc nghiệm',
        'description': 'Hệ thống quiz/trắc nghiệm',
        'icon': 'bi-question-circle',
        'admin_routes': ['admin.quizzes', 'admin.quiz_create', 'admin.quiz_edit', 'admin.quiz_delete',
                         'admin.questions', 'admin.question_create', 'admin.question_edit', 'admin.results'],
        'main_routes': ['main.quiz_start', 'main.quiz_take', 'main.quiz_result'],
        'menu_group': 'interactive'
    },
    'faqs': {
        'name': 'FAQs',
        'description': 'Câu hỏi thường gặp',
        'icon': 'bi-question-circle-fill',
        'admin_routes': ['admin.faqs', 'admin.faq_create', 'admin.faq_edit', 'admin.faq_delete'],
        'main_routes': ['main.faq'],
        'menu_group': 'content'
    },
    'banners': {
        'name': 'Banner',
        'description': 'Quản lý banner trang chủ',
        'icon': 'bi-image',
        'admin_routes': ['admin.banners', 'admin.banner_create', 'admin.banner_edit', 'admin.banner_delete'],
        'main_routes': [],
        'menu_group': 'media'
    },
    'media': {
        'name': 'Thư viện Media',
        'description': 'Quản lý hình ảnh, album',
        'icon': 'bi-folder-fill',
        'admin_routes': ['admin.media', 'admin.media_upload', 'admin.media_edit', 'admin.media_delete'],
        'main_routes': [],
        'menu_group': 'media'
    },
    'chatbot': {
        'name': 'Chatbot AI',
        'description': 'Trợ lý ảo Gemini AI',
        'icon': 'bi-robot',
        'admin_routes': [],
        'main_routes': ['chatbot.send_message', 'chatbot.reset_chat'],
        'menu_group': 'interactive'
    },
    'contacts': {
        'name': 'Liên hệ',
        'description': 'Quản lý tin nhắn liên hệ',
        'icon': 'bi-envelope',
        'admin_routes': ['admin.contacts', 'admin.contact_detail', 'admin.contact_delete'],
        'main_routes': ['main.contact'],
        'menu_group': 'content'
    }
}


# ==================== HELPER FUNCTIONS ====================
def is_feature_enabled(feature_key):
    """
    Kiểm tra xem feature có được bật không

    Args:
        feature_key (str): Key của feature (vd: 'blogs', 'products')

    Returns:
        bool: True nếu feature được bật, False nếu tắt
    """
    if feature_key not in AVAILABLE_FEATURES:
        return True  # Feature không tồn tại trong danh sách = luôn cho phép

    # Lấy từ settings, mặc định là True (enabled)
    setting_key = f'feature_{feature_key}_enabled'
    return get_setting(setting_key, 'true') == 'true'


def get_enabled_features():
    """
    Lấy danh sách các feature đang được bật

    Returns:
        list: Danh sách key của các feature đang enabled
    """
    enabled = []
    for key in AVAILABLE_FEATURES.keys():
        if is_feature_enabled(key):
            enabled.append(key)
    return enabled


def get_feature_info(feature_key):
    """
    Lấy thông tin chi tiết của một feature

    Args:
        feature_key (str): Key của feature

    Returns:
        dict: Thông tin feature hoặc None nếu không tồn tại
    """
    return AVAILABLE_FEATURES.get(feature_key)


def enable_feature(feature_key):
    """
    Bật một feature

    Args:
        feature_key (str): Key của feature cần bật

    Returns:
        bool: True nếu thành công
    """
    if feature_key in AVAILABLE_FEATURES:
        setting_key = f'feature_{feature_key}_enabled'
        set_setting(setting_key, 'true')
        return True
    return False


def disable_feature(feature_key):
    """
    Tắt một feature

    Args:
        feature_key (str): Key của feature cần tắt

    Returns:
        bool: True nếu thành công
    """
    if feature_key in AVAILABLE_FEATURES:
        setting_key = f'feature_{feature_key}_enabled'
        set_setting(setting_key, 'false')
        return True
    return False


# ==================== DECORATOR ====================
def feature_required(feature_key):
    """
    Decorator để bảo vệ route - chỉ cho phép truy cập nếu feature được bật

    Usage:
        @app.route('/blogs')
        @feature_required('blogs')
        def blogs():
            ...

    Args:
        feature_key (str): Key của feature cần kiểm tra
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_feature_enabled(feature_key):
                # Nếu là admin, show thông báo và redirect về dashboard
                if current_user.is_authenticated:
                    flash(f'Chức năng "{AVAILABLE_FEATURES[feature_key]["name"]}" đang bị tắt.', 'warning')
                    return redirect(url_for('admin.dashboard'))
                # Nếu là user thường, trả về 404
                abort(404)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ==================== CONTEXT PROCESSOR HELPER ====================
def get_feature_context():
    """
    Trả về context cho template để kiểm tra feature
    Sử dụng trong app/__init__.py context_processor

    Returns:
        dict: Dictionary chứa hàm is_feature_enabled và danh sách features
    """
    return {
        'is_feature_enabled': is_feature_enabled,
        'enabled_features': get_enabled_features(),
        'all_features': AVAILABLE_FEATURES
    }


# ==================== ADMIN HELPERS ====================
def get_features_by_group():
    """
    Nhóm các features theo menu_group để hiển thị trong admin

    Returns:
        dict: {group_name: [features...]}
    """
    groups = {}
    for key, feature in AVAILABLE_FEATURES.items():
        group = feature.get('menu_group', 'other')
        if group not in groups:
            groups[group] = []

        feature_data = feature.copy()
        feature_data['key'] = key
        feature_data['enabled'] = is_feature_enabled(key)
        groups[group].append(feature_data)

    return groups


# ==================== GROUP LABELS ====================
FEATURE_GROUP_LABELS = {
    'content': '📝 Quản lý nội dung',
    'media': '🎨 Quản lý media',
    'interactive': '🤖 Tính năng tương tác',
    'other': '🔧 Khác'
}