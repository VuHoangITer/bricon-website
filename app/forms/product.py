from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, InputRequired, NumberRange
from app.models.product import Category


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


class ProductForm(FlaskForm):
    """Form quản lý sản phẩm - JSON động + Multi images"""

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

    # ⭐ THÊM FIELD CHO NHIỀU ẢNH
    images_json = HiddenField('Gallery Images')

    is_featured = BooleanField('Sản phẩm nổi bật')
    is_active = BooleanField('Kích hoạt', default=True)

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
- Dòng bắt đầu bằng # sẽ bị bỏ qua (comment)'''
        }
    )

    submit = SubmitField('Lưu sản phẩm')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, '-- Chọn danh mục --')] + [
            (c.id, c.name) for c in Category.query.filter_by(is_active=True).all()
        ]