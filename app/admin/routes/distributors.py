# app/admin/routes/distributors.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.distributor import Distributor
from app.forms.distributor import DistributorForm
from app.decorators import admin_required
from app.admin import admin_bp
import re


@admin_bp.route('/distributors')
@login_required
@admin_required
def distributors():
    """Danh sách nhà phân phối"""
    page = request.args.get('page', 1, type=int)
    city = request.args.get('city', '')
    search = request.args.get('search', '')

    query = Distributor.query

    # Filter theo tỉnh/thành
    if city:
        query = query.filter_by(city=city)

    # Tìm kiếm
    if search:
        query = query.filter(
            db.or_(
                Distributor.name.ilike(f'%{search}%'),
                Distributor.address.ilike(f'%{search}%'),
                Distributor.city.ilike(f'%{search}%')
            )
        )

    distributors = query.order_by(
        Distributor.is_featured.desc(),
        Distributor.name
    ).paginate(page=page, per_page=20, error_out=False)

    cities = Distributor.get_cities()

    return render_template(
        'admin/dai_ly/distributors.html',
        distributors=distributors,
        cities=cities,
        current_city=city,
        search=search
    )


@admin_bp.route('/distributors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_distributor():
    """Thêm nhà phân phối mới"""
    form = DistributorForm()

    if form.validate_on_submit():
        distributor = Distributor()
        form.populate_obj(distributor)

        # Tự động tạo slug
        distributor.generate_slug()

        # Parse coordinates từ iframe nếu có
        if form.map_iframe.data and not form.latitude.data:
            coords = extract_coords_from_iframe(form.map_iframe.data)
            if coords:
                distributor.latitude = coords[0]
                distributor.longitude = coords[1]

        db.session.add(distributor)
        db.session.commit()

        flash('Đã thêm nhà phân phối thành công!', 'success')
        return redirect(url_for('admin.distributors'))

    return render_template('admin/dai_ly/distributor_form.html', form=form, distributor=None)


@admin_bp.route('/distributors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_distributor(id):
    """Sửa thông tin nhà phân phối"""
    distributor = Distributor.query.get_or_404(id)
    form = DistributorForm(obj=distributor)

    if form.validate_on_submit():
        form.populate_obj(distributor)

        # Parse coordinates từ iframe nếu có thay đổi
        if form.map_iframe.data and form.map_iframe.data != distributor.map_iframe:
            coords = extract_coords_from_iframe(form.map_iframe.data)
            if coords:
                distributor.latitude = coords[0]
                distributor.longitude = coords[1]

        db.session.commit()
        flash('Đã cập nhật nhà phân phối thành công!', 'success')
        return redirect(url_for('admin.distributors'))

    return render_template('admin/dai_ly/distributor_form.html', form=form, distributor=distributor)


@admin_bp.route('/distributors/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_distributor(id):
    """Xóa nhà phân phối"""
    distributor = Distributor.query.get_or_404(id)

    try:
        db.session.delete(distributor)
        db.session.commit()
        flash('Đã xóa nhà phân phối thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa: {str(e)}', 'danger')

    return redirect(url_for('admin.distributors'))


@admin_bp.route('/distributors/delete-all', methods=['POST'])
@login_required
@admin_required
def delete_all_distributors():
    """Xóa tất cả nhà phân phối - CHỈ DÙNG TẠM THỜI"""
    try:
        count = Distributor.query.count()
        Distributor.query.delete()
        db.session.commit()
        flash(f'Đã xóa tất cả {count} nhà phân phối!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa tất cả: {str(e)}', 'danger')

    return redirect(url_for('admin.distributors'))


@admin_bp.route('/distributors/<int:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_distributor_active(id):
    """Bật/tắt trạng thái active"""
    distributor = Distributor.query.get_or_404(id)
    distributor.is_active = not distributor.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': distributor.is_active})


@admin_bp.route('/distributors/<int:id>/toggle-featured', methods=['POST'])
@login_required
@admin_required
def toggle_distributor_featured(id):
    """Bật/tắt đại lý nổi bật"""
    distributor = Distributor.query.get_or_404(id)
    distributor.is_featured = not distributor.is_featured
    db.session.commit()
    return jsonify({'success': True, 'is_featured': distributor.is_featured})


def extract_coords_from_iframe(iframe_code):
    """
    Trích xuất tọa độ từ iframe Google Maps
    """
    if not iframe_code:
        return None

    # Tìm tọa độ trong URL - Pattern: !3d{latitude}!4d{longitude}
    pattern = r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)'
    match = re.search(pattern, iframe_code)

    if match:
        lat = float(match.group(1))
        lng = float(match.group(2))
        return (lat, lng)

    # Pattern thay thế: @{latitude},{longitude}
    pattern2 = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
    match2 = re.search(pattern2, iframe_code)

    if match2:
        lat = float(match2.group(1))
        lng = float(match2.group(2))
        return (lat, lng)

    return None