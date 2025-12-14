from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class SettingsForm(FlaskForm):
    """Form quản lý cài đặt hệ thống, chia nhóm"""

    # General Settings
    website_name = StringField('Tên website', validators=[DataRequired()])
    slogan = StringField('Slogan', validators=[Optional()])
    address = StringField('Địa chỉ', validators=[Optional()])
    email = StringField('Email chính', validators=[Email()])
    hotline = StringField('Hotline', validators=[Optional()])
    main_url = StringField('URL chính', validators=[Optional()])
    company_info = TextAreaField('Thông tin công ty', validators=[Optional()])


    # Theme/UI Settings
    logo = FileField('Logo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])
    logo_chatbot = FileField('Logo chatbot', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])

    # SEO & Meta Defaults
    meta_title = StringField('Meta Title mặc định', validators=[DataRequired()])
    meta_description = TextAreaField('Meta Description mặc định', validators=[DataRequired()])
    meta_keywords = StringField('Meta Keywords', validators=[Optional()])

    # FAVICON
    favicon_ico = FileField('Favicon (.ico)', validators=[FileAllowed(['ico'])])
    favicon_png = FileField('Favicon PNG (96x96)', validators=[FileAllowed(['png'])])
    favicon_svg = FileField('Favicon SVG', validators=[FileAllowed(['svg'])])
    apple_touch_icon = FileField('Apple Touch Icon (180x180)', validators=[FileAllowed(['png'])])

    # SEO ON PAGE
    index_meta_description = TextAreaField('Meta Description Trang Chủ', validators=[Length(max=160)])
    about_meta_description = TextAreaField('Meta Description Giới Thiệu', validators=[Length(max=160)])
    contact_meta_description = TextAreaField('Meta Description Liên Hệ', validators=[Length(max=160)])
    products_meta_description = TextAreaField('Meta Description Sản Phẩm', validators=[Length(max=160)])
    blog_meta_description = TextAreaField('Meta Description Blog', validators=[Length(max=160)])
    careers_meta_description = TextAreaField('Meta Description Tuyển Dụng', validators=[Length(max=160)])
    faq_meta_description = TextAreaField('Meta Description FAQ', validators=[Length(max=160)])
    projects_meta_description = TextAreaField('Meta Description Dự Án', validators=[Length(max=160)])
    favicon = FileField('Favicon', validators=[FileAllowed(['ico', 'png'])])
    default_share_image = FileField('Ảnh chia sẻ mặc định', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])

    # Contact & Social Settings
    contact_email = StringField('Email liên hệ', validators=[Email()])
    facebook_url = StringField('Facebook', validators=[Optional()])
    zalo_url = StringField('Zalo', validators=[Optional()])
    tiktok_url = StringField('TikTok', validators=[Optional()])
    youtube_url = StringField('YouTube', validators=[Optional()])
    google_maps = TextAreaField('Bản đồ Google Maps (embed code)', validators=[Optional()])
    working_hours = StringField('Giờ làm việc', validators=[Optional()])
    facebook_messenger_url = StringField('Facebook Messenger', validators=[Optional()])

    branch_addresses = TextAreaField('Danh sách chi nhánh', validators=[Optional()])

    # System & Security Settings
    login_attempt_limit = IntegerField('Giới hạn đăng nhập sai', validators=[NumberRange(min=3, max=10)])
    cache_time = IntegerField('Thời gian cache dữ liệu (giây)', validators=[NumberRange(min=0)])

    # Integration Settings
    cloudinary_api_key = StringField('API Key Cloudinary', validators=[Optional()])
    gemini_api_key = StringField('API Key Gemini/OpenAI', validators=[Optional()])
    google_analytics = StringField('Google Analytics ID', validators=[Optional()])
    shopee_api = StringField('Shopee Integration', validators=[Optional()])
    tiktok_api = StringField('TikTok Integration', validators=[Optional()])
    zalo_oa = StringField('Zalo OA', validators=[Optional()])

    # Content Defaults
    terms_of_service = TextAreaField('Điều khoản dịch vụ', validators=[Optional()])
    shipping_policy = TextAreaField('Chính sách vận chuyển', validators=[Optional()])
    return_policy = TextAreaField('Chính sách đổi trả', validators=[Optional()])
    warranty_policy = TextAreaField('Chính sách bảo hành', validators=[Optional()])
    privacy_policy = TextAreaField('Chính sách bảo mật', validators=[Optional()])


    logo_url = None
    logo_chatbot_url = None
    favicon_url = None
    default_share_image_url = None
    favicon_ico_url = None
    favicon_png_url = None
    favicon_svg_url = None
    apple_touch_icon_url = None


    submit = SubmitField('Lưu cài đặt')
