# app/models/distributor.py
from app import db
from datetime import datetime
from slugify import slugify


class Distributor(db.Model):
    """Model cho nhà phân phối / đại lý"""
    __tablename__ = 'distributors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, index=True)

    # Thông tin liên hệ
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(200))

    # Địa chỉ
    address = db.Column(db.Text)
    ward = db.Column(db.String(100))  # Phường/Xã
    district = db.Column(db.String(100))  # Quận/Huyện
    city = db.Column(db.String(100))  # Tỉnh/Thành phố

    # Tọa độ GPS (giữ lại cho sau này nếu cần)
    latitude = db.Column(db.Float)  # Vĩ độ
    longitude = db.Column(db.Float)  # Kinh độ

    # Google Maps
    map_iframe = db.Column(db.Text)  # Iframe embed từ Google Maps
    map_url = db.Column(db.String(500))  # Link Google Maps (để chỉ đường)

    # Phân loại
    distributor_type = db.Column(db.String(50))  # 'authorized', 'partner', 'retail', etc.

    # Mô tả
    description = db.Column(db.Text)
    working_hours = db.Column(db.String(200))  # Giờ làm việc

    # Hình ảnh
    image_url = db.Column(db.String(500))

    # Trạng thái
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # Đại lý nổi bật

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Distributor {self.name}>'

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'address': self.address,
            'ward': self.ward,
            'district': self.district,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'map_iframe': self.map_iframe,
            'map_url': self.map_url,
            'distributor_type': self.distributor_type,
            'description': self.description,
            'working_hours': self.working_hours,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'full_address': self.get_full_address()
        }

    def get_full_address(self):
        """Lấy địa chỉ đầy đủ"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.ward:
            parts.append(self.ward)
        if self.district:
            parts.append(self.district)
        if self.city:
            parts.append(self.city)
        return ', '.join(parts)

    def generate_slug(self):
        """Tự động tạo slug từ tên"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Distributor.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

    @staticmethod
    def get_cities():
        """Lấy danh sách tỉnh/thành phố"""
        cities = db.session.query(Distributor.city).filter(
            Distributor.city.isnot(None),
            Distributor.is_active == True
        ).distinct().order_by(Distributor.city).all()
        return [city[0] for city in cities if city[0]]

    @staticmethod
    def get_by_city(city):
        """Lấy đại lý theo tỉnh/thành"""
        return Distributor.query.filter_by(
            city=city,
            is_active=True
        ).order_by(
            Distributor.is_featured.desc(),
            Distributor.name
        ).all()