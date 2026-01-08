# File: app/models/product.py

from app import db
from datetime import datetime
from sqlalchemy import event


# ==================== CATEGORY MODEL ====================
class Category(db.Model):
    """Model danh mục sản phẩm"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


# ==================== PRODUCT MODEL ====================
class Product(db.Model):
    """Model sản phẩm - JSON động"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)
    old_price = db.Column(db.Float)
    image = db.Column(db.String(255))
    images = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Legacy SEO fields
    image_alt_text = db.Column(db.String(255))
    image_title = db.Column(db.String(255))
    image_caption = db.Column(db.Text)

    # ⭐ CHỈ GIỮ MỘT FIELD DUY NHẤT CHO THÔNG TIN KỸ THUẬT
    technical_info = db.Column(db.JSON)
    """
    Cấu trúc technical_info (linh hoạt):
    {
        "Thành phần": "Xi măng Portland | Cát thạch anh",
        "Độ bám dính": "≥ 1.0 MPa",
        "pH": "6.5-8.5",
        "Ứng dụng": "Dán gạch | Dán đá",
        ...bất kỳ field nào bạn muốn...
    }
    """

    def __repr__(self):
        return f'<Product {self.name}>'

    def get_media_seo_info(self):
        """Lấy thông tin SEO từ Media Library"""
        if not self.image:
            return None

        from app.models.helpers import get_media_by_image_url
        media = get_media_by_image_url(self.image)

        if media:
            return {
                'alt_text': media.alt_text or self.name,
                'title': media.title or self.name,
                'caption': media.caption
            }

        return {
            'alt_text': self.image_alt_text or self.name,
            'title': self.image_title or self.name,
            'caption': self.image_caption
        }

    def get_images_list(self):
        """Lấy danh sách ảnh từ JSON"""
        if not self.images:
            return []
        try:
            import json
            return json.loads(self.images)
        except:
            return []


# ==================== AUTO CLEAR CACHE EVENTS ====================

@event.listens_for(Category, 'after_insert')
@event.listens_for(Category, 'after_update')
@event.listens_for(Category, 'after_delete')
def clear_category_cache(mapper, connection, target):
    from app import cache_manager
    cache_manager.clear('categories')
    cache_manager.clear('products')


@event.listens_for(Product, 'after_insert')
@event.listens_for(Product, 'after_update')
@event.listens_for(Product, 'after_delete')
def clear_product_cache(mapper, connection, target):
    from app import cache_manager
    cache_manager.clear('products')


# ==================== HELPER FUNCTIONS ====================

def get_cached_categories():
    """Lấy categories từ cache hoặc DB"""
    from app import cache_manager
    cached = cache_manager.get('categories_active')
    if cached is not None:
        return cached

    categories = Category.query.filter_by(is_active=True).all()
    cache_manager.set('categories_active', categories)
    return categories


def get_cached_products(category_id=None, featured_only=False):
    """Lấy products từ cache hoặc DB"""
    from app import cache_manager

    if featured_only:
        cache_key = 'products_featured'
    elif category_id:
        cache_key = f'products_cat_{category_id}'
    else:
        cache_key = 'products_all'

    cached = cache_manager.get(cache_key)
    if cached is not None:
        return cached

    query = Product.query.filter_by(is_active=True)
    if featured_only:
        query = query.filter_by(is_featured=True)
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.all()
    cache_manager.set(cache_key, products)
    return products