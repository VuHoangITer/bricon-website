from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.project_config import PROJECT_TYPE_CHOICES

# ==================== FORM BANNER ====================
class BannerForm(FlaskForm):
    """Form quản lý banner slider"""
    title = StringField('Tiêu đề', validators=[
        Optional(),
        Length(max=200)
    ])
    subtitle = StringField('Phụ đề', validators=[
        Optional(),
        Length(max=255)
    ])
    image = FileField('Hình ảnh Desktop (PC)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'], 'Chỉ chấp nhận ảnh!')
    ])
    image_mobile = FileField('Hình ảnh Mobile (Optional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'], 'Chỉ chấp nhận ảnh!')
    ])
    link = StringField('Link', validators=[Optional(), Length(max=255)])
    button_text = StringField('Text nút', validators=[Optional(), Length(max=50)])
    order = FloatField('Thứ tự', validators=[Optional()])
    is_active = BooleanField('Kích hoạt')
    submit = SubmitField('Lưu banner')

# ==================== FORM SEO MEDIA ====================

class MediaSEOForm(FlaskForm):
    """Form chỉnh sửa SEO cho media (không upload file mới)"""
    alt_text = StringField('Alt Text', validators=[
        DataRequired(message='Alt Text là bắt buộc cho SEO'),
        Length(min=10, max=125, message='Alt Text nên từ 30-125 ký tự')
    ])
    title = StringField('Title', validators=[
        Optional(),
        Length(max=255)
    ])
    caption = TextAreaField('Caption', validators=[
        Optional(),
        Length(max=500)
    ])
    album = StringField('Album', validators=[Optional()])
    submit = SubmitField('Lưu thay đổi')

# ==================== QUẢN LÝ DỰ ÁN ====================
class ProjectForm(FlaskForm):
    """Form cho Dự án tiêu biểu"""
    title = StringField('Tên dự án *', validators=[DataRequired()])
    slug = StringField('Slug (URL)', validators=[DataRequired()])
    client = StringField('Khách hàng')
    location = StringField('Địa điểm')
    year = IntegerField('Năm thực hiện', validators=[Optional()])

    description = TextAreaField('Mô tả ngắn')
    content = TextAreaField('Nội dung chi tiết')

    image = FileField('Ảnh đại diện', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Chỉ chấp nhận file ảnh!')
    ])

    project_type = SelectField(
        'Loại dự án',
        choices=PROJECT_TYPE_CHOICES,
        validators=[DataRequired()]
    )

    area = StringField('Diện tích')
    products_used = TextAreaField('Sản phẩm sử dụng')

    is_featured = BooleanField('Dự án nổi bật')
    is_active = BooleanField('Kích hoạt', default=True)

    submit = SubmitField('Lưu dự án')