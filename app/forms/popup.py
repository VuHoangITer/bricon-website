"""
Form quản lý Popup
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField, FileField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import Optional, NumberRange


class PopupForm(FlaskForm):
    """Form tạo/sửa popup - CHỈ ẢNH VÀ LINK"""

    # Nội dung
    image = FileField('Ảnh Banner',
                      render_kw={'accept': 'image/*'})

    link = StringField('Link khi click ảnh',
                       validators=[Optional()],
                       render_kw={'placeholder': 'VD: /san-pham, tel:1900636294, https://example.com'})

    # Hiển thị
    display_pages = SelectField('Hiển thị trang',
                                choices=[
                                    ('all', '🌐 Tất cả các trang'),
                                    ('homepage', '🏠 Chỉ trang chủ'),
                                    ('products', '📦 Trang sản phẩm'),
                                    ('blogs', '📰 Trang tin tức'),
                                    ('contact', '📞 Trang liên hệ')
                                ],
                                default='all')

    # ❌ BỎ position

    # Tần suất
    frequency = SelectField('Tần suất hiển thị',
                            choices=[
                                ('once_per_day', '📅 Mỗi ngày 1 lần'),
                                ('once_per_session', '🔄 Mỗi phiên 1 lần'),
                                ('every_visit', '♾️ Mỗi lần vào trang')
                            ],
                            default='once_per_day')

    delay_seconds = IntegerField('Delay (giây)',
                                 validators=[Optional(), NumberRange(min=0, max=60)],
                                 default=2,
                                 render_kw={'placeholder': '2'})

    # Schedule
    start_date = DateTimeLocalField('Ngày bắt đầu',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[Optional()])

    end_date = DateTimeLocalField('Ngày kết thúc',
                                  format='%Y-%m-%dT%H:%M',
                                  validators=[Optional()])

    # Status
    is_active = BooleanField('Kích hoạt', default=True)