"""
Admin Routes - Features Management
Quản lý bật/tắt các chức năng của hệ thống
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.admin import admin_bp
from app.decorators import permission_required
from app.models.features import (
    AVAILABLE_FEATURES,
    get_features_by_group,
    FEATURE_GROUP_LABELS,
    enable_feature,
    disable_feature,
    is_feature_enabled
)


@admin_bp.route('/features')
@login_required
@permission_required('manage_features')
def features():
    """
    Trang quản lý bật/tắt chức năng
    Hiển thị danh sách tất cả features và trạng thái của chúng
    """
    features_by_group = get_features_by_group()

    return render_template(
        'admin/features/features.html',
        features_by_group=features_by_group,
        group_labels=FEATURE_GROUP_LABELS,
        title='Quản lý chức năng'
    )


@admin_bp.route('/features/toggle/<feature_key>', methods=['POST'])
@login_required
@permission_required('manage_features')
def feature_toggle(feature_key):
    """
    API để bật/tắt một feature

    Args:
        feature_key (str): Key của feature cần toggle

    Returns:
        JSON response với status
    """
    if feature_key not in AVAILABLE_FEATURES:
        return jsonify({
            'success': False,
            'message': 'Feature không tồn tại'
        }), 404

    # Lấy action từ request (enable/disable)
    action = request.form.get('action', 'toggle')

    current_status = is_feature_enabled(feature_key)

    if action == 'enable' or (action == 'toggle' and not current_status):
        success = enable_feature(feature_key)
        new_status = True
        message = f'Đã BẬT chức năng "{AVAILABLE_FEATURES[feature_key]["name"]}"'
    else:
        success = disable_feature(feature_key)
        new_status = False
        message = f'Đã TẮT chức năng "{AVAILABLE_FEATURES[feature_key]["name"]}"'

    if success:
        flash(message, 'success')
    else:
        flash('Không thể thay đổi trạng thái feature', 'danger')

    return redirect(url_for('admin.features'))



@admin_bp.route('/features/bulk-toggle', methods=['POST'])
@login_required
@permission_required('manage_features')
def features_bulk_toggle():
    """
    Bật/tắt nhiều features cùng lúc

    Form data:
        features: list of feature keys
        action: 'enable' hoặc 'disable'
    """
    feature_keys = request.form.getlist('features')
    action = request.form.get('action')

    if not feature_keys or action not in ['enable', 'disable']:
        flash('Dữ liệu không hợp lệ', 'danger')
        return redirect(url_for('admin.features'))

    success_count = 0
    for key in feature_keys:
        if key in AVAILABLE_FEATURES:
            if action == 'enable':
                if enable_feature(key):
                    success_count += 1
            else:
                if disable_feature(key):
                    success_count += 1

    if success_count > 0:
        action_text = 'BẬT' if action == 'enable' else 'TẮT'
        flash(f'Đã {action_text} thành công {success_count} chức năng', 'success')
    else:
        flash('Không có chức năng nào được thay đổi', 'warning')

    return redirect(url_for('admin.features'))