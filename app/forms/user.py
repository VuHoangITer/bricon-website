from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from app.models.user import User


# ==================== FORM USER ====================
class UserForm(FlaskForm):
    """Form quản lý người dùng với RBAC - Role filtering được xử lý trong route"""
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ')
    ])
    password = PasswordField('Mật khẩu', validators=[
        Optional(),
        Length(min=6, message='Mật khẩu tối thiểu 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        EqualTo('password', message='Mật khẩu không khớp')
    ])

    role_id = SelectField('Vai trò', coerce=int, validators=[
        DataRequired(message='Vui lòng chọn vai trò')
    ])
    submit = SubmitField('Lưu người dùng')

    def __init__(self, user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = user

        # ⚠️ QUAN TRỌNG: KHÔNG khởi tạo role_id.choices ở đây
        # Sẽ được gán trong route dựa trên quyền của current_user
        # Điều này đảm bảo mỗi user chỉ thấy roles họ có quyền gán

    def validate_username(self, username):
        """Kiểm tra username có trùng không"""
        user = User.query.filter_by(username=username.data).first()
        if user and (self.user is None or user.id != self.user.id):
            raise ValidationError('Tên đăng nhập đã tồn tại')

    def validate_email(self, email):
        """Kiểm tra email có trùng không"""
        user = User.query.filter_by(email=email.data).first()
        if user and (self.user is None or user.id != self.user.id):
            raise ValidationError('Email đã tồn tại')


# ==================== RoleForm ====================
class RoleForm(FlaskForm):
    """Form quản lý Role"""
    name = StringField('Tên role (code)', validators=[
        DataRequired(message='Vui lòng nhập tên role'),
        Length(min=3, max=50)
    ])
    display_name = StringField('Tên hiển thị', validators=[
        DataRequired(message='Vui lòng nhập tên hiển thị'),
        Length(min=3, max=100)
    ])
    description = StringField('Mô tả', validators=[Optional()])
    priority = SelectField('Độ ưu tiên', coerce=int, choices=[
        (1000, 'Developer (1000)'),
        (100, 'Cao nhất (100)'),
        (70, 'Cao (70)'),
        (50, 'Trung bình (50)'),
        (30, 'Thấp (30)'),
        (10, 'Thấp nhất (10)')
    ])
    color = SelectField('Màu badge', choices=[
        ('dark', 'Đen (Developer)'),
        ('danger', 'Đỏ (Admin)'),
        ('primary', 'Xanh dương (Editor)'),
        ('info', 'Xanh nhạt (Moderator)'),
        ('success', 'Xanh lá'),
        ('warning', 'Vàng'),
        ('secondary', 'Xám (User)')
    ])
    is_active = BooleanField('Kích hoạt', default=True)
    submit = SubmitField('Lưu vai trò')


# ==================== PermissionForm ====================
class PermissionForm(FlaskForm):
    """Form quản lý Permission"""
    name = StringField('Tên permission (code)', validators=[
        DataRequired(message='Vui lòng nhập tên permission'),
        Length(min=3, max=100)
    ])
    display_name = StringField('Tên hiển thị', validators=[
        DataRequired(message='Vui lòng nhập tên hiển thị'),
        Length(min=3, max=100)
    ])
    description = StringField('Mô tả', validators=[Optional()])
    category = SelectField('Danh mục', choices=[
        ('products', 'Sản phẩm'),
        ('blogs', 'Blog'),
        ('media', 'Media'),
        ('users', 'Người dùng'),
        ('contacts', 'Liên hệ'),
        ('projects', 'Dự án'),
        ('jobs', 'Tuyển dụng'),
        ('system', 'Hệ thống'),
        ('quiz', 'Quiz'),
    ])
    icon = StringField('Icon (Bootstrap)', validators=[
        Optional(),
        Length(max=50)
    ])
    is_active = BooleanField('Kích hoạt', default=True)
    submit = SubmitField('Lưu quyền')