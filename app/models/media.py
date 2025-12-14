from app import db
from datetime import datetime


# ==================== BANNER MODEL ====================
class Banner(db.Model):
    """Model banner slider trang chủ"""
    __tablename__ = 'banners'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(255))
    image = db.Column(db.String(255), nullable=False)
    image_mobile = db.Column(db.String(255))  # Ảnh Mobile (optional)
    link = db.Column(db.String(255))
    button_text = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Banner {self.title}>'

    def get_media_seo_info(self):
        """Lấy thông tin SEO từ Media Library cho Banner Desktop"""
        if not self.image:
            return None

        from app.models.helpers import get_media_by_image_url
        media = get_media_by_image_url(self.image)

        if media:
            return {
                'alt_text': media.alt_text or self.title,
                'title': media.title or self.title,
                'caption': media.caption or self.subtitle
            }
        return {
            'alt_text': self.title,
            'title': self.title,
            'caption': self.subtitle
        }

    def get_mobile_media_seo_info(self):
        """Lấy thông tin SEO cho ảnh Mobile"""
        if not self.image_mobile:
            return self.get_media_seo_info()  # Fallback về ảnh desktop

        from app.models.helpers import get_media_by_image_url
        media = get_media_by_image_url(self.image_mobile)

        if media:
            return {
                'alt_text': media.alt_text or f"{self.title} - Mobile",
                'title': media.title or self.title,
                'caption': media.caption or self.subtitle
            }

        return self.get_media_seo_info()


# ==================== MEDIA MODEL ====================
class Media(db.Model):
    """Model quản lý hình ảnh/media files với SEO optimization"""
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    # SEO Fields
    alt_text = db.Column(db.String(255))
    title = db.Column(db.String(255))
    caption = db.Column(db.Text)

    # Organization
    album = db.Column(db.String(100))

    # Metadata
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Media {self.filename}>'

    def get_url(self):
        return self.filepath if self.filepath.startswith('/') else f'/{self.filepath}'

    def get_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0


# ==================== PROJECT MODEL ====================
class Project(db.Model):
    """Model cho Dự án tiêu biểu"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    client = db.Column(db.String(200))  # Tên khách hàng
    location = db.Column(db.String(200))  # Địa điểm
    year = db.Column(db.Integer)  # Năm thực hiện

    description = db.Column(db.Text)  # Mô tả ngắn
    content = db.Column(db.Text)  # Nội dung chi tiết

    image = db.Column(db.String(300))  # Ảnh đại diện
    gallery = db.Column(db.Text)  # JSON array các ảnh gallery

    # Thông tin dự án
    project_type = db.Column(db.String(100))  # Loại dự án: Nhà ở, Văn phòng, Khách sạn...
    area = db.Column(db.String(100))  # Diện tích
    products_used = db.Column(db.Text)  # Sản phẩm đã sử dụng

    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

    def get_gallery_images(self):
        """Parse gallery JSON"""
        if self.gallery:
            import json
            try:
                return json.loads(self.gallery)
            except:
                return []
        return []

    def get_media_seo_info(self):
        """
        Lấy thông tin SEO từ Media Library cho Project

        Priority:
        1. Media Library
        2. Fallback về title/description của Project
        """
        if not self.image:
            return None

        from app.models.helpers import get_media_by_image_url
        media = get_media_by_image_url(self.image)

        if media:
            return {
                'alt_text': media.alt_text or self.title,
                'title': media.title or self.title,
                'caption': media.caption or self.description
            }

        # Fallback: dùng thông tin từ Project
        return {
            'alt_text': f"Dự án {self.title}" + (f" - {self.location}" if self.location else ""),
            'title': f"{self.title} ({self.year})" if self.year else self.title,
            'caption': self.description or f"Dự án {self.project_type} tại {self.location}"
        }