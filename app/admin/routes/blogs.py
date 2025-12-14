from flask import render_template, request, flash, redirect, url_for, jsonify
from app import db
from app.models.content import Blog
from app.forms.content import BlogForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.helpers import get_image_from_form
from flask_login import login_user, logout_user, login_required, current_user
from app.models.features import feature_required
from datetime import datetime
import pytz


# ==================== LIST ====================
@admin_bp.route('/blogs')
@permission_required('view_blogs')
@feature_required('blogs')
def blogs():
    """
    📋 Danh sách blog với filter theo status
    - Phân trang 20 items/page
    - Sắp xếp theo created_at (mới nhất)
    - Filter: all, draft, scheduled, published
    """
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')

    query = Blog.query

    # Filter theo status
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    blogs = query.order_by(Blog.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # Đếm số lượng theo status
    stats = {
        'all': Blog.query.count(),
        'draft': Blog.query.filter_by(status='draft').count(),
        'scheduled': Blog.query.filter_by(status='scheduled').count(),
        'published': Blog.query.filter_by(status='published').count(),
    }

    return render_template('admin/tin_tuc/blogs.html',
                           blogs=blogs,
                           status_filter=status_filter,
                           stats=stats)


# ==================== ADD ====================
@admin_bp.route('/blogs/add', methods=['GET', 'POST'])
@permission_required('create_blog')
@feature_required('blogs')
def add_blog():
    form = BlogForm()

    if form.validate_on_submit():
        image_path = get_image_from_form(form.image, 'image', folder='blogs')

        blog = Blog(
            title=form.title.data,
            slug=form.slug.data,
            excerpt=form.excerpt.data,
            content=form.content.data,
            image=image_path,
            author=form.author.data or current_user.username,
            is_featured=form.is_featured.data,
        )

        # ==================== XỬ LÝ PUBLISH MODE ====================
        publish_mode = form.publish_mode.data

        if publish_mode == 'publish_now':
            # Đăng ngay
            blog.publish()
            flash('✅ Đã đăng bài viết thành công!', 'success')

        elif publish_mode == 'schedule':
            # Lên lịch đăng
            scheduled_time = form.scheduled_at.data

            if not scheduled_time:
                flash('⚠️ Vui lòng chọn thời gian đăng bài!', 'warning')
                return render_template('admin/tin_tuc/blog_form.html',
                                       form=form,
                                       title='Thêm bài viết')

            # Convert từ local time (Việt Nam) sang UTC
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

            # Kiểm tra nếu scheduled_time là naive datetime
            if scheduled_time.tzinfo is None:
                scheduled_time = vn_tz.localize(scheduled_time)

            # Chuyển sang UTC
            scheduled_time_utc = scheduled_time.astimezone(pytz.utc).replace(tzinfo=None)

            # Kiểm tra thời gian trong quá khứ
            if scheduled_time_utc <= datetime.utcnow():
                flash('⚠️ Thời gian đăng phải ở tương lai!', 'warning')
                return render_template('admin/tin_tuc/blog_form.html',
                                       form=form,
                                       title='Thêm bài viết')

            blog.schedule(scheduled_time_utc)
            flash(f'⏰ Đã lên lịch đăng bài lúc {scheduled_time.strftime("%d/%m/%Y %H:%M")}!', 'info')

        else:  # draft
            # Lưu nháp
            blog.save_as_draft()
            flash('📝 Đã lưu bài viết dưới dạng bản nháp!', 'info')

        db.session.add(blog)
        db.session.commit()

        return redirect(url_for('admin.blogs'))

    return render_template('admin/tin_tuc/blog_form.html',
                           form=form,
                           title='Thêm bài viết')


# ==================== EDIT ====================
@admin_bp.route('/blogs/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('edit_all_blogs')
@feature_required('blogs')
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    form = BlogForm(obj=blog)

    # Pre-fill publish_mode dựa vào status hiện tại
    if request.method == 'GET':
        if blog.status == 'published':
            form.publish_mode.data = 'publish_now'
        elif blog.status == 'scheduled':
            form.publish_mode.data = 'schedule'
            # Convert UTC về Việt Nam cho form
            if blog.scheduled_at:
                vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
                utc_time = pytz.utc.localize(blog.scheduled_at)
                vn_time = utc_time.astimezone(vn_tz)
                form.scheduled_at.data = vn_time.replace(tzinfo=None)
        else:
            form.publish_mode.data = 'draft'

    if form.validate_on_submit():
        new_image = get_image_from_form(form.image, 'image', folder='blogs')
        if new_image:
            blog.image = new_image

        blog.title = form.title.data
        blog.slug = form.slug.data
        blog.excerpt = form.excerpt.data
        blog.content = form.content.data
        blog.author = form.author.data
        blog.is_featured = form.is_featured.data

        # ==================== XỬ LÝ PUBLISH MODE ====================
        publish_mode = form.publish_mode.data

        if publish_mode == 'publish_now':
            blog.publish()
            flash('✅ Đã cập nhật và đăng bài viết!', 'success')

        elif publish_mode == 'schedule':
            scheduled_time = form.scheduled_at.data

            if not scheduled_time:
                flash('⚠️ Vui lòng chọn thời gian đăng bài!', 'warning')
                return render_template('admin/tin_tuc/blog_form.html',
                                       form=form,
                                       title='Sửa bài viết',
                                       blog=blog)

            # Convert từ local time sang UTC
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            if scheduled_time.tzinfo is None:
                scheduled_time = vn_tz.localize(scheduled_time)
            scheduled_time_utc = scheduled_time.astimezone(pytz.utc).replace(tzinfo=None)

            if scheduled_time_utc <= datetime.utcnow():
                flash('⚠️ Thời gian đăng phải ở tương lai!', 'warning')
                return render_template('admin/tin_tuc/blog_form.html',
                                       form=form,
                                       title='Sửa bài viết',
                                       blog=blog)

            blog.schedule(scheduled_time_utc)
            flash(f'⏰ Đã lên lịch đăng bài lúc {scheduled_time.strftime("%d/%m/%Y %H:%M")}!', 'info')

        else:  # draft
            blog.save_as_draft()
            flash('📝 Đã lưu bài viết dưới dạng bản nháp!', 'info')

        db.session.commit()

        return redirect(url_for('admin.blogs'))

    return render_template('admin/tin_tuc/blog_form.html',
                           form=form,
                           title='Sửa bài viết',
                           blog=blog)


# ==================== DELETE ====================
@admin_bp.route('/blogs/delete/<int:id>')
@permission_required('delete_blog')
@feature_required('blogs')
def delete_blog(id):
    """🗑️ Xóa blog"""
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()

    flash('Đã xóa bài viết thành công!', 'success')
    return redirect(url_for('admin.blogs'))


# ==================== QUICK PUBLISH (AJAX) ====================
@admin_bp.route('/blogs/quick-publish/<int:id>', methods=['POST'])
@permission_required('edit_all_blogs')
@feature_required('blogs')
def quick_publish_blog(id):
    """🚀 Publish bài viết ngay lập tức (AJAX)"""
    blog = Blog.query.get_or_404(id)

    if blog.status == 'published':
        return jsonify({'success': False, 'message': 'Bài viết đã được đăng rồi'}), 400

    blog.publish()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Đã đăng bài viết thành công!',
        'status': blog.status_label
    })

# ==================== DEBUG: TEST SCHEDULER ====================
@admin_bp.route('/blogs/debug-scheduler', methods=['GET'])
@permission_required('view_blogs')
@feature_required('blogs')
def debug_scheduler():
    """🧪 Debug scheduler - Kiểm tra bài viết scheduled"""
    from app.scheduler import test_scheduled_posts
    result = test_scheduled_posts()
    return jsonify(result)


# ==================== DEBUG: FORCE PUBLISH ====================
@admin_bp.route('/blogs/force-publish-scheduled', methods=['POST'])
@permission_required('edit_all_blogs')
@feature_required('blogs')
def force_publish_scheduled():
    """🚀 Force chạy scheduler ngay"""
    try:
        from app.scheduler import publish_scheduled_posts
        publish_scheduled_posts()
        return jsonify({
            'success': True,
            'message': 'Đã chạy scheduler thành công! Kiểm tra danh sách bài viết.'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500