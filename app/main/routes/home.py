from flask import render_template, g
from app.main import main_bp
from app.models import Settings
from app.models.product import Product, Category
from app.models.media import Banner, Project
from app.models.content import Blog
from app.models.popup import Popup  # ✅ THÊM import Popup
from sqlalchemy.orm import load_only
from app.models.settings import get_setting
from app.models.features import is_feature_enabled


@main_bp.route('/')
def index():
    """Trang chủ - Chỉ load data của features đang enabled"""

    # ✅ THÊM: Load popup cho trang chủ
    g.popup = Popup.get_active_popup(page='homepage')

    # Banner - luôn hiển thị (hoặc check nếu cần)
    banners = []
    if is_feature_enabled('banners'):
        banners = Banner.query.filter_by(is_active=True).order_by(Banner.order).all()

    # Sản phẩm - chỉ load nếu feature enabled
    featured_products = []
    latest_products = []
    categories = []

    if is_feature_enabled('products'):
        featured_products = Product.query.filter_by(
            is_featured=True,
            is_active=True
        ).limit(6).all()

        latest_products = Product.query.filter_by(
            is_active=True
        ).order_by(Product.created_at.desc()).limit(6).all()

        # Query danh mục sản phẩm
        categories = Category.query.filter_by(
            is_active=True
        ).order_by(Category.name).all()

    # Blog - chỉ load nếu feature enabled
    featured_blogs = []
    if is_feature_enabled('blogs'):
        featured_blogs = (Blog.query
                          .options(load_only(Blog.slug, Blog.title, Blog.created_at, Blog.image))
                          .filter_by(is_featured=True, is_active=True)
                          .order_by(Blog.created_at.desc())
                          ).limit(3).all()

    # Dự án - chỉ load nếu feature enabled
    featured_projects = []
    if is_feature_enabled('projects'):
        featured_projects = Project.query.filter_by(
            is_featured=True,
            is_active=True
        ).order_by(Project.created_at.desc()).limit(6).all()

    return render_template('public/index.html',
                           banners=banners,
                           featured_products=featured_products,
                           latest_products=latest_products,
                           featured_blogs=featured_blogs,
                           featured_projects=featured_projects,
                           categories=categories)


@main_bp.route('/gioi-thieu')
def about():
    """Trang giới thiệu"""
    # ✅ THÊM: Load popup cho trang giới thiệu (nếu cần)
    g.popup = Popup.get_active_popup(page='all')
    return render_template('public/about.html')


@main_bp.route('/chinh-sach', defaults={'policy_slug': None})
@main_bp.route('/chinh-sach/<policy_slug>')
def policy(policy_slug):
    """
    Hiển thị trang chính sách.
    Nếu có policy_slug, chỉ hiển thị chính sách đó.
    Nếu không, hiển thị chính sách đầu tiên có nội dung.
    """
    # ✅ THÊM: Load popup
    g.popup = Popup.get_active_popup(page='all')

    # Lấy tất cả các cài đặt chính sách từ DB
    all_policies_settings = {
        'dieu-khoan-dich-vu': {
            'name': 'Điều khoản dịch vụ',
            'icon': 'bi-file-earmark-text',
            'content': get_setting('terms_of_service', '')
        },
        'van-chuyen': {
            'name': 'Chính sách vận chuyển',
            'icon': 'bi-truck',
            'content': get_setting('shipping_policy', '')
        },
        'doi-tra': {
            'name': 'Chính sách đổi trả',
            'icon': 'bi-arrow-repeat',
            'content': get_setting('return_policy', '')
        },
        'bao-hanh': {
            'name': 'Chính sách bảo hành',
            'icon': 'bi-shield-check',
            'content': get_setting('warranty_policy', '')
        },
        'bao-mat': {
            'name': 'Chính sách bảo mật',
            'icon': 'bi-lock',
            'content': get_setting('privacy_policy', '')
        }
    }

    # Chỉ giữ lại các chính sách có nội dung
    available_policies = {
        slug: data for slug, data in all_policies_settings.items() if data['content']
    }

    # Nếu không có chính sách nào, hiển thị trang trống
    if not available_policies:
        return render_template('public/policy.html',
                               policies={},
                               active_policy_slug=None,
                               active_policy_data=None)

    # Nếu không có slug nào được cung cấp, chọn slug đầu tiên làm mặc định
    if policy_slug is None:
        active_policy_slug = next(iter(available_policies))
    else:
        active_policy_slug = policy_slug

    active_policy_data = available_policies[active_policy_slug]

    return render_template(
        'public/policy.html',
        policies=available_policies,
        active_policy_slug=active_policy_slug,
        active_policy_data=active_policy_data
    )


@main_bp.route('/bang-mau')
def color_chart():
    """Trang bảng màu sản phẩm"""
    g.popup = Popup.get_active_popup(page='all')
    return render_template('public/color_chart.html')


@main_bp.route('/huong-dan-thi-cong')
def installation_guide():
    """Trang hướng dẫn thi công"""
    g.popup = Popup.get_active_popup(page='all')
    return render_template('public/installation_guide.html')