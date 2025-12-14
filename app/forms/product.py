# File: app/forms/product.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, InputRequired, NumberRange
from app.models.product import Category


# ==================== FORM DANH MỤC ====================
class CategoryForm(FlaskForm):
    """Form quản lý danh mục"""
    name = StringField('Tên danh mục', validators=[
        DataRequired(message='Vui lòng nhập tên danh mục'),
        Length(min=2, max=100)
    ])
    slug = StringField('Slug (URL)', validators=[
        DataRequired(message='Vui lòng nhập slug'),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Mô tả', validators=[Optional()])
    image = FileField('Hình ảnh', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'], 'Chỉ chấp nhận ảnh!')
    ])
    is_active = BooleanField('Kích hoạt')
    submit = SubmitField('Lưu danh mục')


# ==================== FORM SẢN PHẨM ====================
class ProductForm(FlaskForm):
    """Form quản lý sản phẩm - JSON động"""

    # ========== THÔNG TIN CƠ BẢN ==========
    name = StringField('Tên sản phẩm', validators=[
        DataRequired(message='Vui lòng nhập tên sản phẩm'),
        Length(min=2, max=200)
    ])

    slug = StringField('Slug (URL)', validators=[
        DataRequired(message='Vui lòng nhập slug'),
        Length(min=2, max=200)
    ])

    description = TextAreaField('Mô tả sản phẩm', validators=[Optional()])

    price = FloatField('Giá bán', validators=[
        InputRequired(message='Vui lòng nhập giá'),
        NumberRange(min=0, message='Giá phải >= 0')
    ])

    old_price = FloatField('Giá cũ', validators=[Optional(), NumberRange(min=0)])

    category_id = SelectField('Danh mục', coerce=int, validators=[
        DataRequired(message='Vui lòng chọn danh mục')
    ])

    image = FileField('Hình ảnh chính', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'], 'Chỉ chấp nhận ảnh!')
    ])

    is_featured = BooleanField('Sản phẩm nổi bật')
    is_active = BooleanField('Kích hoạt', default=True)

    # ⭐ THÔNG TIN KỸ THUẬT - JSON ĐỘNG (THAY THẾ TẤT CẢ FIELDS CŨ)
    technical_info_raw = TextAreaField(
        'Thông tin kỹ thuật',
        validators=[Optional()],
        render_kw={
            'rows': 20,
            'class': 'font-monospace',
            'placeholder': '''Nhập theo định dạng: Tên trường: Giá trị

Hướng dẫn:
- Mỗi dòng 1 thông tin
- Dùng dấu | để phân tách list items
- Dòng bắt đầu bằng # sẽ bị bỏ qua (comment)

Ví dụ:

# Thông tin cơ bản
Thành phần: Xi măng Portland | Cát thạch anh | Phụ gia polymer
Quy trình sản xuất: Sản xuất theo quy trình khép kín, kiểm soát chất lượng nghiêm ngặt
Tiêu chuẩn: TCVN 7957:2008, ISO 9001

# Thông số kỹ thuật
Độ bám dính: ≥ 1.0 MPa
Độ mịn: ≤ 45 µm
pH: 6.5-8.5
Độ ẩm: ≤ 80%
Thời gian đóng rắn: 24-48 giờ

# Ứng dụng và đóng gói
Ứng dụng: Dán gạch ceramic | Dán đá ốp tường | Chà ron gạch
Quy cách đóng gói: Bao 25kg | Thùng 20kg | Bao 5kg
Hạn sử dụng: 12 tháng kể từ ngày sản xuất

# Màu sắc
Màu sắc: Trắng | Xám | Vàng chanh | Đen'''
        }
    )

    submit = SubmitField('Lưu sản phẩm')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Load danh mục vào dropdown
        self.category_id.choices = [(0, '-- Chọn danh mục --')] + [
            (c.id, c.name) for c in Category.query.filter_by(is_active=True).all()
        ]