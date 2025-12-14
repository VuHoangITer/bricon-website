"""
Routes quản lý Popup
"""
from flask import render_template, request, flash, redirect, url_for, jsonify
from app import db
from app.models.popup import Popup
from app.forms.popup import PopupForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.helpers import get_image_from_form
from flask_login import current_user
import pytz


@admin_bp.route('/popups')
@permission_required('manage_banners')
def popups():
    """📋 Danh sách popup"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')

    query = Popup.query

    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    popups = query.order_by(Popup.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    stats = {
        'all': Popup.query.count(),
        'active': Popup.query.filter_by(is_active=True).count(),
        'inactive': Popup.query.filter_by(is_active=False).count(),
    }

    return render_template('admin/popups/list.html',
                           popups=popups,
                           status_filter=status_filter,
                           stats=stats)


@admin_bp.route('/popups/add', methods=['GET', 'POST'])
@permission_required('manage_banners')
def add_popup():
    """➕ Tạo popup mới"""
    form = PopupForm()

    if form.validate_on_submit():
        # Upload image (BẮT BUỘC khi tạo mới)
        image_path = get_image_from_form(form.image, 'image', folder='popups')

        if not image_path:
            flash('⚠️ Vui lòng chọn ảnh!', 'warning')
            return render_template('admin/popups/form.html', form=form, title='Tạo Popup Mới')

        # Convert datetime
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        start_date = form.start_date.data
        end_date = form.end_date.data

        if start_date:
            if start_date.tzinfo is None:
                start_date = vn_tz.localize(start_date)
            start_date = start_date.astimezone(pytz.utc).replace(tzinfo=None)

        if end_date:
            if end_date.tzinfo is None:
                end_date = vn_tz.localize(end_date)
            end_date = end_date.astimezone(pytz.utc).replace(tzinfo=None)

        # Tạo popup
        popup = Popup(
            image=image_path,
            link=form.link.data,
            display_pages=form.display_pages.data,
            # ❌ BỎ position
            frequency=form.frequency.data,
            delay_seconds=form.delay_seconds.data,
            start_date=start_date,
            end_date=end_date,
            is_active=form.is_active.data,
            created_by=current_user.username
        )

        db.session.add(popup)
        db.session.commit()

        flash('✅ Đã tạo popup thành công!', 'success')
        return redirect(url_for('admin.popups'))

    return render_template('admin/popups/form.html',
                           form=form,
                           title='Tạo Popup Mới')


@admin_bp.route('/popups/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_banners')
def edit_popup(id):
    """✏️ Sửa popup"""
    popup = Popup.query.get_or_404(id)
    form = PopupForm(obj=popup)

    # Pre-fill datetime
    if request.method == 'GET':
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

        if popup.start_date:
            utc_time = pytz.utc.localize(popup.start_date)
            vn_time = utc_time.astimezone(vn_tz)
            form.start_date.data = vn_time.replace(tzinfo=None)

        if popup.end_date:
            utc_time = pytz.utc.localize(popup.end_date)
            vn_time = utc_time.astimezone(vn_tz)
            form.end_date.data = vn_time.replace(tzinfo=None)

    if form.validate_on_submit():
        # Upload new image (CHỈ KHI CÓ FILE MỚI)
        new_image = get_image_from_form(form.image, 'image', folder='popups')
        if new_image:
            popup.image = new_image

        # Convert datetime
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        start_date = form.start_date.data
        end_date = form.end_date.data

        if start_date:
            if start_date.tzinfo is None:
                start_date = vn_tz.localize(start_date)
            start_date = start_date.astimezone(pytz.utc).replace(tzinfo=None)

        if end_date:
            if end_date.tzinfo is None:
                end_date = vn_tz.localize(end_date)
            end_date = end_date.astimezone(pytz.utc).replace(tzinfo=None)

        # Update
        popup.link = form.link.data
        popup.display_pages = form.display_pages.data
        # ❌ BỎ position
        popup.frequency = form.frequency.data
        popup.delay_seconds = form.delay_seconds.data
        popup.start_date = start_date
        popup.end_date = end_date
        popup.is_active = form.is_active.data

        db.session.commit()

        flash('✅ Đã cập nhật popup!', 'success')
        return redirect(url_for('admin.popups'))

    return render_template('admin/popups/form.html',
                           form=form,
                           title='Sửa Popup',
                           popup=popup)


@admin_bp.route('/popups/delete/<int:id>')
@permission_required('manage_banners')
def delete_popup(id):
    """🗑️ Xóa popup"""
    popup = Popup.query.get_or_404(id)
    db.session.delete(popup)
    db.session.commit()

    flash('Đã xóa popup thành công!', 'success')
    return redirect(url_for('admin.popups'))


@admin_bp.route('/popups/toggle/<int:id>', methods=['POST'])
@permission_required('manage_banners')
def toggle_popup(id):
    """🔄 Bật/tắt popup (AJAX)"""
    popup = Popup.query.get_or_404(id)
    popup.is_active = not popup.is_active
    db.session.commit()

    return jsonify({
        'success': True,
        'is_active': popup.is_active,
        'message': f"Đã {'bật' if popup.is_active else 'tắt'} popup"
    })


@admin_bp.route('/api/popup/view/<int:id>', methods=['POST'])
def track_popup_view(id):
    """📊 Track popup view"""
    popup = Popup.query.get_or_404(id)
    popup.increment_views()
    return jsonify({'success': True})


@admin_bp.route('/api/popup/click/<int:id>', methods=['POST'])
def track_popup_click(id):
    """📊 Track popup click"""
    popup = Popup.query.get_or_404(id)
    popup.increment_clicks()
    return jsonify({'success': True})