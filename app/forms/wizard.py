# File: app/forms/wizard.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


# ==================== WIZARD FORM ====================
class WizardForm(FlaskForm):
    """Form quản lý Wizard"""
    name = StringField('Tên Wizard', validators=[
        DataRequired(message='Vui lòng nhập tên wizard'),
        Length(min=2, max=200)
    ])

    slug = StringField('Slug (URL)', validators=[
        DataRequired(message='Vui lòng nhập slug'),
        Length(min=2, max=200)
    ])

    description = TextAreaField('Mô tả', validators=[Optional()],
                                render_kw={'rows': 3})

    icon = StringField('Icon Class', validators=[Optional()],
                      render_kw={'placeholder': 'bi-magic'})

    is_active = BooleanField('Kích hoạt', default=True)
    is_default = BooleanField('Đặt làm wizard mặc định')

    submit = SubmitField('Lưu Wizard')


# ==================== WIZARD STEP FORM ====================
class WizardStepForm(FlaskForm):
    """Form quản lý Step trong Wizard"""
    step_number = IntegerField('Bước số', validators=[
        DataRequired(message='Vui lòng nhập số thứ tự bước'),
        NumberRange(min=1, message='Số bước phải >= 1')
    ])

    question_text = StringField('Câu hỏi', validators=[
        DataRequired(message='Vui lòng nhập câu hỏi'),
        Length(min=5, max=500)
    ])

    description = TextAreaField('Mô tả thêm', validators=[Optional()],
                               render_kw={'rows': 2})

    step_type = SelectField('Loại câu hỏi', choices=[
        ('single_choice', 'Chọn một đáp án'),
        ('multiple_choice', 'Chọn nhiều đáp án')
    ], validators=[DataRequired()])

    is_required = BooleanField('Bắt buộc', default=True)

    submit = SubmitField('Lưu Step')


# ==================== WIZARD OPTION FORM ====================
class WizardOptionForm(FlaskForm):
    """Form quản lý Option trong Step"""
    option_text = StringField('Nội dung lựa chọn', validators=[
        DataRequired(message='Vui lòng nhập nội dung'),
        Length(min=2, max=200)
    ])

    description = StringField('Mô tả ngắn', validators=[
        Optional(),
        Length(max=500)
    ])

    icon_class = StringField('Icon Class', validators=[Optional()],
                            render_kw={'placeholder': 'bi-house-fill'})

    emoji = StringField('Emoji', validators=[Optional()],
                       render_kw={'placeholder': '🏠', 'maxlength': 10})

    tags = TextAreaField('Tags (JSON)', validators=[Optional()],
                        render_kw={
                            'rows': 3,
                            'placeholder': '["interior", "residential", "waterproof"]'
                        })

    order = IntegerField('Thứ tự hiển thị', validators=[
        Optional(),
        NumberRange(min=0)
    ], default=0)

    submit = SubmitField('Lưu Option')