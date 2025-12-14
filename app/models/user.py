from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(db.Model, UserMixin):
    """Model cho người dùng với RBAC"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))

    # ✅ THAY ĐỔI: Thêm role_id (foreign key)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=None)

    # ✅ GIỮ LẠI: is_admin (deprecated field cho tương thích ngược)
    # Khi migrate, chuyển users cũ: is_admin=True → role_id=1 (admin)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    blogs = db.relationship('Blog', backref='author_obj', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash và lưu mật khẩu"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)

    # ==================== RBAC METHODS ====================

    # ✅ THÊM: TIMEZONE PROPERTIES
    @property
    def created_at_vn(self):
        """Lấy created_at theo múi giờ Việt Nam"""
        from app.utils import utc_to_vn
        return utc_to_vn(self.created_at)

    @property
    def updated_at_vn(self):
        """Lấy updated_at theo múi giờ Việt Nam"""
        from app.utils import utc_to_vn
        return utc_to_vn(self.updated_at)

    @property
    def is_developer(self):
        """
        Kiểm tra user có phải Developer không
        """
        return self.role_obj and self.role_obj.name == 'developer'

    @property
    def is_admin(self):
        """
        Backward compatibility với code cũ
        Trả về True nếu role là 'admin' hoặc 'developer'
        """
        return self.role_obj and self.role_obj.name in ['admin', 'developer']

    @property
    def role_name(self):
        """Lấy tên role (developer, admin, editor, moderator, user)"""
        return self.role_obj.name if self.role_obj else 'user'

    @property
    def role_display_name(self):
        """Lấy tên hiển thị role (Lập trình viên, Quản trị viên, ...)"""
        return self.role_obj.display_name if self.role_obj else 'Người dùng'

    @property
    def role_color(self):
        """Lấy màu badge role (dark, danger, primary, info, secondary)"""
        return self.role_obj.color if self.role_obj else 'secondary'

    def has_permission(self, permission_name):
        """
        Kiểm tra user có quyền cụ thể không

        Args:
            permission_name (str): Tên permission (vd: 'manage_products')

        Returns:
            bool: True nếu có quyền
        """
        if not self.role_obj or not self.is_active:
            return False
        return self.role_obj.has_permission(permission_name)

    def has_any_permission(self, *permission_names):
        """
        Kiểm tra user có ít nhất 1 trong các quyền

        Args:
            *permission_names: Danh sách tên permissions

        Returns:
            bool: True nếu có ít nhất 1 quyền
        """
        return any(self.has_permission(perm) for perm in permission_names)

    def has_all_permissions(self, *permission_names):
        """
        Kiểm tra user có tất cả các quyền

        Args:
            *permission_names: Danh sách tên permissions

        Returns:
            bool: True nếu có đủ tất cả quyền
        """
        return all(self.has_permission(perm) for perm in permission_names)

    def get_permissions(self):
        """
        Lấy danh sách tất cả permissions của user

        Returns:
            list: Danh sách Permission objects
        """
        if not self.role_obj:
            return []
        return self.role_obj.permissions.filter_by(is_active=True).all()

    def assign_role(self, role_name):
        """
        Gán role cho user

        Args:
            role_name (str): Tên role (developer, admin, editor, moderator, user)
        """
        from app.models.rbac import Role
        role = Role.query.filter_by(name=role_name).first()
        if role:
            self.role_id = role.id
            return True
        return False


# ==================== USER LOADER ====================
from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user cho Flask-Login"""
    return User.query.get(int(user_id))