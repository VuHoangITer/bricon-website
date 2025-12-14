"""
👥 Users Management Routes - WITH ROLE HIERARCHY SECURITY
"""
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.models.user import User
from app.forms.user import UserForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.models.rbac import Role


# ==================== SECURITY HELPERS ====================
def can_manage_user(target_user):
    """
    Kiểm tra user hiện tại có thể quản lý target_user không
    Rule: Chỉ được quản lý user có role priority THẤP HƠN role của mình

    Args:
        target_user: User object cần kiểm tra

    Returns:
        bool: True nếu có quyền quản lý
    """
    if not current_user.is_authenticated:
        return False

    current_role = current_user.role_obj
    target_role = target_user.role_obj

    if not current_role:
        return False

    # Không ai được sửa/xóa Developer (trừ chính Developer)
    if target_role and target_role.name == 'developer':
        return current_role.name == 'developer'

    # Các role khác: chỉ được quản lý role có priority thấp hơn
    if not target_role:
        return True  # User không có role thì được phép quản lý

    return current_role.priority > target_role.priority


def get_manageable_roles():
    """
    Lấy danh sách roles mà user hiện tại có thể gán cho người khác

    Returns:
        list: Danh sách Role objects
    """
    if not current_user.is_authenticated or not current_user.role_obj:
        return []

    current_priority = current_user.role_obj.priority
    current_role_name = current_user.role_obj.name

    # Developer thấy tất cả roles (bao gồm cả Developer)
    if current_role_name == 'developer':
        return Role.query.filter_by(is_active=True).order_by(Role.priority.desc()).all()

    # Các role khác: CHỈ thấy roles có priority THẤP HƠN
    # KHÔNG BAO GIỜ thấy Developer
    return Role.query.filter(
        Role.is_active == True,
        Role.priority < current_priority,
        Role.name != 'developer'  # ẨN Developer khỏi danh sách
    ).order_by(Role.priority.desc()).all()


def get_visible_users():
    """
    Lấy danh sách users mà user hiện tại có thể xem

    Returns:
        Query: SQLAlchemy query object
    """
    if not current_user.is_authenticated or not current_user.role_obj:
        return User.query.filter_by(id=0)  # Empty query

    current_priority = current_user.role_obj.priority
    current_role_name = current_user.role_obj.name

    # Developer thấy tất cả users
    if current_role_name == 'developer':
        return User.query

    # Các role khác: CHỈ thấy users có role priority THẤP HƠN hoặc BẰNG
    # KHÔNG thấy Developer users
    developer_role = Role.query.filter_by(name='developer').first()

    if developer_role:
        return User.query.filter(
            (User.role_id != developer_role.id) | (User.role_id == None)
        ).join(Role, User.role_id == Role.id, isouter=True).filter(
            (Role.priority < current_priority) | (Role.id == None)
        )

    return User.query.join(Role, User.role_id == Role.id, isouter=True).filter(
        (Role.priority < current_priority) | (Role.id == None)
    )


# ==================== QUẢN LÝ NGƯỜI DÙNG ====================
@admin_bp.route('/users')
@permission_required('view_users')
def users():
    """Danh sách người dùng - CHỈ hiển thị users có quyền xem"""
    role_filter = request.args.get('role', '')

    # Lấy query với filter bảo mật
    query = get_visible_users()

    # Filter theo role (nếu có)
    if role_filter:
        role_obj = Role.query.filter_by(name=role_filter).first()
        if role_obj and can_manage_user_with_role(role_obj):
            query = query.filter(User.role_id == role_obj.id)

    users = query.order_by(User.created_at.desc()).all()

    # Lấy stats
    stats = {
        'total_users': query.count(),
        'roles': get_manageable_roles()
    }

    return render_template('admin/nguoi_dung/users.html', users=users, stats=stats)


def can_manage_user_with_role(role):
    """Kiểm tra có thể quản lý users với role này không"""
    if not current_user.role_obj:
        return False

    # Developer thấy tất cả
    if current_user.role_obj.name == 'developer':
        return True

    # Không thấy Developer role
    if role.name == 'developer':
        return False

    # Chỉ thấy role có priority thấp hơn
    return current_user.role_obj.priority > role.priority


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@permission_required('manage_users')
def add_user():
    """Thêm người dùng mới - CHỈ được gán roles có quyền thấp hơn"""
    form = UserForm()

    # ✅ GHI ĐÈ: Chỉ hiển thị roles được phép gán
    manageable_roles = get_manageable_roles()
    form.role_id.choices = [(r.id, r.display_name) for r in manageable_roles]

    if not form.role_id.choices:
        flash('⛔ Bạn không có quyền gán bất kỳ role nào!', 'danger')
        return redirect(url_for('admin.users'))

    if form.validate_on_submit():
        # 🔒 SECURITY CHECK: Kiểm tra role_id có trong danh sách được phép không
        allowed_role_ids = [r.id for r in manageable_roles]
        if form.role_id.data not in allowed_role_ids:
            flash('⛔ Bạn không có quyền gán role này!', 'danger')
            return render_template('admin/nguoi_dung/user_form.html', form=form, title='Thêm người dùng')

        # Kiểm tra password
        if not form.password.data:
            flash('Vui lòng nhập mật khẩu!', 'danger')
            return render_template('admin/nguoi_dung/user_form.html', form=form, title='Thêm người dùng')

        # Tạo user mới
        user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role_id.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'✅ Đã thêm người dùng "{user.username}" với vai trò "{user.role_display_name}"!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/nguoi_dung/user_form.html', form=form, title='Thêm người dùng')


@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_users')
def edit_user(id):
    """Sửa người dùng - CHỈ được sửa users có priority thấp hơn"""
    user = User.query.get_or_404(id)

    # 🔒 SECURITY CHECK 1: Kiểm tra quyền quản lý user này
    if not can_manage_user(user):
        flash('⛔ Bạn không có quyền chỉnh sửa người dùng này!', 'danger')
        return redirect(url_for('admin.users'))

    form = UserForm(user=user, obj=user)

    # ✅ GHI ĐÈ: Chỉ hiển thị roles được phép gán
    manageable_roles = get_manageable_roles()
    form.role_id.choices = [(r.id, r.display_name) for r in manageable_roles]

    if form.validate_on_submit():
        # 🔒 SECURITY CHECK 2: Kiểm tra role_id mới có hợp lệ không
        allowed_role_ids = [r.id for r in manageable_roles]
        if form.role_id.data not in allowed_role_ids:
            flash('⛔ Bạn không có quyền gán role này!', 'danger')
            return render_template('admin/nguoi_dung/user_form.html',
                                 form=form,
                                 title='Sửa người dùng',
                                 user=user)

        # 🔒 SECURITY CHECK 3: Không cho phép tự nâng cấp role của mình
        if user.id == current_user.id:
            old_priority = user.role_obj.priority if user.role_obj else 0
            new_role = Role.query.get(form.role_id.data)
            new_priority = new_role.priority if new_role else 0

            if new_priority > old_priority:
                flash('⛔ Bạn không thể tự nâng cấp quyền của chính mình!', 'danger')
                return render_template('admin/nguoi_dung/user_form.html',
                                     form=form,
                                     title='Sửa người dùng',
                                     user=user)

        # Cập nhật thông tin
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role_id.data

        # Chỉ đổi password nếu có nhập
        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()

        flash(f'✅ Đã cập nhật người dùng "{user.username}"!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/nguoi_dung/user_form.html',
                         form=form,
                         title='Sửa người dùng',
                         user=user)


@admin_bp.route('/users/delete/<int:id>')
@permission_required('manage_users')
def delete_user(id):
    """Xóa người dùng - CHỈ được xóa users có priority thấp hơn"""
    # 🔒 SECURITY CHECK 1: Không được xóa chính mình
    if id == current_user.id:
        flash('⛔ Không thể xóa tài khoản của chính mình!', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(id)

    # 🔒 SECURITY CHECK 2: Kiểm tra quyền xóa user này
    if not can_manage_user(user):
        flash('⛔ Bạn không có quyền xóa người dùng này!', 'danger')
        return redirect(url_for('admin.users'))

    # 🔒 SECURITY CHECK 3: Không được xóa Developer (double check)
    if user.role_obj and user.role_obj.name == 'developer':
        flash('⛔ Không thể xóa tài khoản Developer!', 'danger')
        return redirect(url_for('admin.users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'✅ Đã xóa người dùng "{username}" thành công!', 'success')
    return redirect(url_for('admin.users'))