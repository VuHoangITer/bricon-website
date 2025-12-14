"""
📊 Enhanced Dashboard & Welcome Routes
- Dashboard: Cho Admin/Editor với analytics đầy đủ
- Welcome: Cho User thường
✅ TÍCH HỢP FEATURE FLAGS
"""

from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import db
from app.models.product import Product, Category
from app.models.content import Blog, FAQ
from app.models.contact import Contact
from app.models.media import Media, Banner, Project
from app.models.job import Job
from app.models.quiz import Quiz, QuizAttempt
from app.decorators import permission_required
from app.admin import admin_bp
from app.utils import get_vn_now
from app.models.features import is_feature_enabled

# ==================== DASHBOARD ====================
@admin_bp.route('/dashboard')
@permission_required('view_dashboard')
def dashboard():
    """
    Dashboard đầy đủ - CHỈ cho Admin & Editor
    Với analytics nâng cao và biểu đồ
    ✅ Tự động ẩn stats của features bị tắt
    """
    # Kiểm tra quyền - chỉ Admin/Editor vào được
    if not current_user.has_any_permission('manage_users', 'manage_products', 'manage_categories'):
        return redirect(url_for('admin.welcome'))

    # ==================== BASIC STATS - CHỈ LOAD FEATURES ENABLED ====================
    stats = {}

    # ✅ Products
    if is_feature_enabled('products'):
        stats['products'] = Product.query.count()
        stats['categories'] = Category.query.count()

    # ✅ Blogs
    if is_feature_enabled('blogs'):
        stats['blogs'] = Blog.query.count()

    # ✅ Contacts
    if is_feature_enabled('contacts'):
        stats['contacts_unread'] = Contact.query.filter_by(is_read=False).count()

    # ✅ Projects
    if is_feature_enabled('projects'):
        stats['projects'] = Project.query.count()

    # ✅ FAQs
    if is_feature_enabled('faqs'):
        stats['faqs'] = FAQ.query.filter_by(is_active=True).count()

    # ✅ Jobs/Careers
    if is_feature_enabled('careers'):
        stats['jobs'] = Job.query.filter_by(is_active=True).count()

    # ✅ Media
    if is_feature_enabled('media'):
        stats['media'] = Media.query.count()

    # ✅ Quiz
    if is_feature_enabled('quiz'):
        stats['quizzes'] = Quiz.query.filter_by(is_active=True).count()

    # ==================== TREND CALCULATIONS ====================
    now = get_vn_now()
    last_month_start = now.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_start.replace(day=1)
    this_month_start = now.replace(day=1)

    def calculate_trend(model, date_field='created_at'):
        """Tính % tăng/giảm so với tháng trước"""
        this_month = model.query.filter(
            getattr(model, date_field) >= this_month_start
        ).count()

        last_month = model.query.filter(
            getattr(model, date_field) >= last_month_start,
            getattr(model, date_field) < this_month_start
        ).count()

        if last_month == 0:
            return 100 if this_month > 0 else 0

        trend = ((this_month - last_month) / last_month) * 100
        return round(trend, 1)

    trends = {}

    # ✅ Chỉ tính trend cho features enabled
    if is_feature_enabled('products'):
        trends['products'] = calculate_trend(Product)
    if is_feature_enabled('blogs'):
        trends['blogs'] = calculate_trend(Blog)
    if is_feature_enabled('contacts'):
        trends['contacts'] = calculate_trend(Contact)
    if is_feature_enabled('projects'):
        trends['projects'] = calculate_trend(Project)

    # ==================== RECENT ITEMS ====================
    recent_products = []
    recent_contacts = []
    recent_blogs = []

    if is_feature_enabled('products'):
        recent_products = Product.query.order_by(desc(Product.created_at)).limit(5).all()
    if is_feature_enabled('contacts'):
        recent_contacts = Contact.query.order_by(desc(Contact.created_at)).limit(5).all()
    if is_feature_enabled('blogs'):
        recent_blogs = Blog.query.order_by(desc(Blog.created_at)).limit(5).all()

    # ==================== ACTIVITY TIMELINE ====================
    activities = []

    # ✅ Products
    if is_feature_enabled('products'):
        for p in Product.query.order_by(desc(Product.created_at)).limit(3).all():
            activities.append({
                'type': 'product',
                'icon': 'bi-box-seam',
                'color': 'warning',
                'title': f'Sản phẩm mới: {p.name}',
                'time': p.created_at,
                'link': url_for('admin.edit_product', id=p.id)
            })

    # ✅ Blogs
    if is_feature_enabled('blogs'):
        for b in Blog.query.order_by(desc(Blog.created_at)).limit(3).all():
            activities.append({
                'type': 'blog',
                'icon': 'bi-newspaper',
                'color': 'info',
                'title': f'Bài viết mới: {b.title}',
                'time': b.created_at,
                'link': url_for('admin.edit_blog', id=b.id)
            })

    # ✅ Contacts
    if is_feature_enabled('contacts'):
        for c in Contact.query.order_by(desc(Contact.created_at)).limit(3).all():
            activities.append({
                'type': 'contact',
                'icon': 'bi-envelope',
                'color': 'danger' if not c.is_read else 'secondary',
                'title': f'Liên hệ từ: {c.name}',
                'time': c.created_at,
                'link': url_for('admin.view_contact', id=c.id)
            })

    # Sort by time and take top 10
    activities.sort(key=lambda x: x['time'], reverse=True)
    activities = activities[:10]

    # ==================== TOP PERFORMERS ====================
    top_products = []
    top_blogs = []

    if is_feature_enabled('products'):
        top_products = Product.query.order_by(desc(Product.views)).limit(5).all()
    if is_feature_enabled('blogs'):
        top_blogs = Blog.query.order_by(desc(Blog.views)).limit(5).all()

    # ==================== CATEGORY DISTRIBUTION ====================
    category_stats = []
    if is_feature_enabled('products'):
        category_stats = db.session.query(
            Category.name,
            func.count(Product.id).label('count')
        ).outerjoin(Product).group_by(Category.id, Category.name).all()

    # ==================== BLOG VIEWS CHART (7 days) ====================
    blog_views_data = []
    if is_feature_enabled('blogs'):
        seven_days_ago = now - timedelta(days=7)

        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            count = Blog.query.filter(
                func.date(Blog.created_at) == date.date()
            ).count()
            blog_views_data.append({
                'date': date.strftime('%d/%m'),
                'count': count
            })

    # ==================== CONTACT STATS (4 weeks) ====================
    contact_weekly = []
    if is_feature_enabled('contacts'):
        def get_week_label(weeks_ago):
            """Tạo nhãn tuần với khoảng ngày cụ thể"""
            week_start = now - timedelta(days=now.weekday() + (weeks_ago * 7))
            week_end = week_start + timedelta(days=6)
            return f"{week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m')}"

        for i in range(4):
            week_start = now - timedelta(days=now.weekday() + ((3-i) * 7))
            week_end = week_start + timedelta(days=7)

            count = Contact.query.filter(
                Contact.created_at >= week_start,
                Contact.created_at < week_end
            ).count()

            contact_weekly.append({
                'week': get_week_label(3-i),
                'count': count
            })

    return render_template('admin/dashboard.html',
                         stats=stats,
                         trends=trends,
                         recent_products=recent_products,
                         recent_contacts=recent_contacts,
                         recent_blogs=recent_blogs,
                         activities=activities,
                         top_products=top_products,
                         top_blogs=top_blogs,
                         category_stats=category_stats,
                         blog_views_data=blog_views_data,
                         contact_weekly=contact_weekly)


# ==================== WELCOME USER ====================
@admin_bp.route('/welcome')
@login_required
def welcome():
    """Trang chào mừng cho User thường"""
    if current_user.has_any_permission('manage_users', 'manage_products', 'manage_categories'):
        return redirect(url_for('admin.dashboard'))

    # ✅ Chỉ hiển thị contact count nếu feature enabled
    total_contacts = 0
    if is_feature_enabled('contacts') and current_user.has_any_permission('view_contacts', 'manage_contacts'):
        total_contacts = Contact.query.filter_by(is_read=False).count()

    return render_template('admin/auth/welcome.html', total_contacts=total_contacts)