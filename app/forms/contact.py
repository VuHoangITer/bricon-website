# ==================== FORM LIÊN HỆ ====================
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ContactForm(FlaskForm):
    """Form liên hệ từ khách hàng"""
    name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ tên'),
        Length(min=2, max=100, message='Họ tên từ 2-100 ký tự')
    ])
    email = StringField('Email', validators=[
        Optional(),
        Email(message='Email không hợp lệ')
    ])
    phone = StringField('Số điện thoại', validators=[
        DataRequired(message='Vui lòng nhập số điện thoại'),
        Length(max=20)
    ])
    subject = StringField('Tiêu đề', validators=[
        Optional(),
        Length(max=200)
    ])
    message = TextAreaField('Nội dung', validators=[
        DataRequired(message='Vui lòng nhập nội dung'),
        Length(min=10, message='Nội dung tối thiểu 10 ký tự')
    ])
    submit = SubmitField('Gửi liên hệ')