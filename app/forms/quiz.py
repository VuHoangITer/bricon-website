# ==================== QUIZ FORMS ====================
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class QuizForm(FlaskForm):
    """Form quản lý Quiz (Đề thi)"""
    title = StringField('Tên đề thi *', validators=[
        DataRequired(message='Vui lòng nhập tên đề thi'),
        Length(min=5, max=200, message='Tên đề thi từ 5-200 ký tự')
    ])

    slug = StringField('Slug (URL)', validators=[
        Optional(),
        Length(max=200)
    ])

    description = TextAreaField('Mô tả đề thi', validators=[
        Optional()
    ], render_kw={'rows': 4, 'placeholder': 'Mô tả ngắn gọn về nội dung đề thi'})

    duration_minutes = IntegerField('Thời gian làm bài (phút)', validators=[
        DataRequired(message='Vui lòng nhập thời gian'),
        NumberRange(min=1, max=180, message='Thời gian từ 1-180 phút')
    ], default=30)

    pass_score = IntegerField('Điểm đạt (%)', validators=[
        DataRequired(message='Vui lòng nhập điểm đạt'),
        NumberRange(min=0, max=100, message='Điểm từ 0-100')
    ], default=70)

    # Cài đặt hiển thị
    show_correct_answers = BooleanField('Hiển thị đáp án sau khi nộp', default=True)
    shuffle_questions = BooleanField('Xáo trộn câu hỏi', default=False)
    shuffle_answers = BooleanField('Xáo trộn đáp án', default=True)

    # Phân loại
    category = SelectField('Danh mục', choices=[
        ('', '-- Chọn danh mục --'),
        ('Phong-van', 'Phỏng vấn'),
        ('San-pham', 'Sản phẩm'),
        ('CRM', 'CRM'),
        ('QTUX', 'Quy tắc ứng xử TELESALES'),
        ('noi-quy-nvcskh', 'NỘI QUY NV CSKH'),
        ('Ke-toan', 'Kế toán')
    ])

    is_active = BooleanField('Kích hoạt', default=True)

    submit = SubmitField('Lưu đề thi')


class QuestionForm(FlaskForm):
    """Form thêm/sửa câu hỏi"""
    quiz_id = IntegerField('Quiz ID', validators=[DataRequired()])

    question_text = TextAreaField('Nội dung câu hỏi *', validators=[
        DataRequired(message='Vui lòng nhập nội dung câu hỏi'),
        Length(min=1, message='Câu hỏi tối thiểu 1 ký tự')
    ], render_kw={'rows': 4})

    question_type = SelectField('Loại câu hỏi', choices=[
        ('multiple_choice', 'Trắc nghiệm (Multiple Choice)'),
        ('true_false', 'Đúng/Sai')
    ], default='multiple_choice')

    points = IntegerField('Điểm', validators=[
        DataRequired(message='Vui lòng nhập điểm'),
        NumberRange(min=1, max=10, message='Điểm từ 1-10')
    ], default=1)

    explanation = TextAreaField('Giải thích đáp án (optional)', validators=[
        Optional()
    ], render_kw={'rows': 3, 'placeholder': 'Giải thích tại sao đáp án này đúng'})

    submit = SubmitField('Lưu câu hỏi')


class QuizStartForm(FlaskForm):
    """Form nhập thông tin trước khi làm bài"""
    user_name = StringField('Họ và tên *', validators=[
        DataRequired(message='Vui lòng nhập họ tên'),
        Length(min=2, max=200, message='Họ tên từ 2-200 ký tự')
    ])

    user_email = StringField('Email', validators=[
        Optional(),
        Email(message='Email không hợp lệ')
    ])

    user_phone = StringField('Số điện thoại', validators=[
        Optional(),
        Length(max=20)
    ])

    submit = SubmitField('Bắt đầu làm bài')