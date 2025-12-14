from flask import render_template, request, flash, redirect, url_for
from app import db
from app.models.media import Banner
from app.forms.media import BannerForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.helpers import get_image_from_form
from app.models.features import feature_required

# ==================== LIST ====================
@admin_bp.route('/banners')
@permission_required('manage_banners')
@feature_required('banners')
def banners():
    """
    📋 Danh sách banner
    - Sắp xếp theo order (tăng dần)
    - Hiển thị preview ảnh desktop + mobile
    """
    banners = Banner.query.order_by(Banner.order).all()
    return render_template('admin/banner/banners.html', banners=banners)


# ==================== ADD ====================
@admin_bp.route('/banners/add', methods=['GET', 'POST'])
@permission_required('manage_banners')
@feature_required('banners')
def add_banner():
    """
    ➕ Thêm banner mới

    Upload flow:
    1. Chọn ảnh desktop (bắt buộc)
    2. Chọn ảnh mobile (optional)
    3. Upload qua get_image_from_form (Media Picker + Upload)
    """
    form = BannerForm()

    if form.validate_on_submit():
        # ✅ ĐỌC ẢNH DESKTOP - ƯU TIÊN MEDIA LIBRARY
        image_path = request.form.get('selected_image_path')  # Từ Media Library
        if not image_path:
            # Nếu không có, đọc từ upload
            image_path = get_image_from_form(form.image, 'image', folder='banners')

        if not image_path:
            flash('Vui lòng chọn hoặc upload ảnh banner!', 'danger')
            return render_template('admin/banner/banner_form.html', form=form, title='Thêm banner')

        # ✅ ĐỌC ẢNH MOBILE - ƯU TIÊN MEDIA LIBRARY
        image_mobile_path = request.form.get('selected_image_mobile_path')  # Từ Media Library
        if not image_mobile_path and form.image_mobile.data:
            # Nếu không có từ library, đọc từ upload
            image_mobile_path = get_image_from_form(form.image_mobile, 'image_mobile', folder='banners/mobile')

        banner = Banner(
            title=form.title.data,
            subtitle=form.subtitle.data,
            image=image_path,
            image_mobile=image_mobile_path,
            link=form.link.data,
            button_text=form.button_text.data,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )

        db.session.add(banner)
        db.session.commit()

        flash('Đã thêm banner thành công!', 'success')
        return redirect(url_for('admin.banners'))

    return render_template('admin/banner/banner_form.html', form=form, title='Thêm banner')


# ==================== EDIT ====================
@admin_bp.route('/banners/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_banners')
@feature_required('banners')
def edit_banner(id):
    """
    ✏️ Sửa banner

    FEATURES đặc biệt:
    - Checkbox "Xóa ảnh Desktop" (delete_desktop_image)
    - Checkbox "Xóa ảnh Mobile" (delete_mobile_image)
    - Có thể xóa riêng lẻ từng ảnh
    - Upload ảnh mới sẽ thay thế ảnh cũ
    """
    banner = Banner.query.get_or_404(id)
    form = BannerForm(obj=banner)

    if form.validate_on_submit():
        # ✅ XỬ LÝ XÓA ẢNH DESKTOP
        delete_desktop = request.form.get('delete_desktop_image') == '1'
        if delete_desktop:
            banner.image = None
            flash('Đã xóa ảnh Desktop', 'info')

        # ✅ XỬ LÝ XÓA ẢNH MOBILE
        delete_mobile = request.form.get('delete_mobile_image') == '1'
        if delete_mobile:
            banner.image_mobile = None
            flash('Đã xóa ảnh Mobile', 'info')

        # ✅ CẬP NHẬT ẢNH DESKTOP
        if not delete_desktop:
            # Ưu tiên đọc từ Media Library
            new_image = request.form.get('selected_image_path')
            if not new_image:
                # Nếu không có, đọc từ upload
                new_image = get_image_from_form(form.image, 'image', folder='banners')

            if new_image:
                banner.image = new_image

        # ✅ CẬP NHẬT ẢNH MOBILE
        if not delete_mobile:
            # Ưu tiên đọc từ Media Library
            new_image_mobile = request.form.get('selected_image_mobile_path')
            if not new_image_mobile:
                # Nếu không có, đọc từ upload
                new_image_mobile = get_image_from_form(form.image_mobile, 'image_mobile', folder='banners/mobile')

            if new_image_mobile:
                banner.image_mobile = new_image_mobile

        banner.title = form.title.data
        banner.subtitle = form.subtitle.data
        banner.link = form.link.data
        banner.button_text = form.button_text.data
        banner.order = form.order.data or 0
        banner.is_active = form.is_active.data

        db.session.commit()

        flash('Đã cập nhật banner thành công!', 'success')
        return redirect(url_for('admin.banners'))

    return render_template('admin/banner/banner_form.html', form=form, title='Sửa banner', banner=banner)


# ==================== DELETE ====================
@admin_bp.route('/banners/delete/<int:id>')
@permission_required('manage_banners')
@feature_required('banners')
def delete_banner(id):
    """
    🗑️ Xóa banner

    Note: Không xóa file ảnh (để tái sử dụng trong Media Library)
    """
    banner = Banner.query.get_or_404(id)
    db.session.delete(banner)
    db.session.commit()

    flash('Đã xóa banner thành công!', 'success')
    return redirect(url_for('admin.banners'))