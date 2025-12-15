# app/forms/distributor.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, URL


class DistributorForm(FlaskForm):
    """Form tạo/sửa nhà phân phối"""

    # Thông tin cơ bản
    name = StringField('Tên nhà phân phối', validators=[DataRequired()])

    # Liên hệ
    phone = StringField('Số điện thoại', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    website = StringField('Website', validators=[Optional(), URL()])

    # Địa chỉ
    address = StringField('Địa chỉ', validators=[DataRequired()])
    ward = StringField('Phường/Xã', validators=[Optional()])
    district = StringField('Quận/Huyện', validators=[Optional()])
    city = StringField('Tỉnh/Thành phố', validators=[DataRequired()])

    # Tọa độ - CHỈ 1 Ô INPUT
    coordinates = StringField('Tọa độ (Lat, Lng)', validators=[Optional()])
    latitude = HiddenField()
    longitude = HiddenField()

    # Google Maps
    map_iframe = TextAreaField('Google Maps Iframe', validators=[Optional()])
    map_url = StringField('Link Google Maps', validators=[Optional(), URL()])

    # Thông tin thêm
    description = TextAreaField('Mô tả', validators=[Optional()])
    working_hours = StringField('Giờ làm việc', validators=[Optional()])
    image_url = StringField('URL hình ảnh', validators=[Optional()])

    # Trạng thái
    is_active = BooleanField('Kích hoạt', default=True)
    is_featured = BooleanField('Đại lý nổi bật', default=False)