from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, Optional

# ==================== QUẢN LÍ TUYỂN DỤNG ====================
class JobForm(FlaskForm):
    """Form cho Tuyển dụng"""
    title = StringField('Vị trí tuyển dụng *', validators=[DataRequired()])
    slug = StringField('Slug (URL)', validators=[DataRequired()])

    department = StringField('Phòng ban')
    location = StringField('Địa điểm làm việc *', validators=[DataRequired()])

    job_type = SelectField('Hình thức', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Hợp đồng'),
        ('internship', 'Thực tập')
    ])

    level = SelectField('Cấp bậc', choices=[
        ('intern', 'Thực tập sinh'),
        ('Fresher', 'Mới ra trường'),
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Team Lead'),
        ('manager', 'Manager'),
        ('Tất cả mọi cấp bậc', 'Tất cả mọi cấp bậc'),
    ])

    salary = StringField('Mức lương', validators=[DataRequired()])
    experience = StringField('Kinh nghiệm yêu cầu')

    description = TextAreaField('Mô tả công việc', validators=[DataRequired()])
    requirements = TextAreaField('Yêu cầu ứng viên')
    benefits = TextAreaField('Quyền lợi')

    deadline = DateField('Hạn nộp hồ sơ', validators=[Optional()])
    contact_email = StringField('Email nhận CV', validators=[DataRequired(), Email()])

    is_active = BooleanField('Đang tuyển', default=True)
    is_urgent = BooleanField('Tuyển gấp')

    submit = SubmitField('Lưu tin tuyển dụng')