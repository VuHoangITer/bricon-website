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


# ==================== AUTO CLEAR CACHE EVENTS ====================

@event.listens_for(Category, 'after_insert')
@event.listens_for(Category, 'after_update')
@event.listens_for(Category, 'after_delete')
def clear_category_cache(mapper, connection, target):
    """Clear cache khi category thay đổi"""
    from app import cache_manager

    # Clear tất cả cache liên quan đến categories
    cache_manager.clear('categories')
    cache_manager.clear('categories_active')

    # Clear luôn products vì products có liên kết với categories
    cache_manager.clear('products')
    cache_manager.clear('products_all')
    cache_manager.clear('products_featured')


@event.listens_for(Product, 'after_insert')
@event.listens_for(Product, 'after_update')
@event.listens_for(Product, 'after_delete')
def clear_product_cache(mapper, connection, target):
    """Clear cache khi product thay đổi"""
    from app import cache_manager

    # ✅ Clear TẤT CẢ các cache keys liên quan đến products
    cache_manager.clear('products')
    cache_manager.clear('products_all')
    cache_manager.clear('products_featured')
    cache_manager.clear('admin_products_all')

    # Clear cache theo category nếu có
    if target.category_id:
        cache_manager.clear(f'products_cat_{target.category_id}')


# ==================== HELPER FUNCTIONS ====================

def get_cached_categories():
    """Lấy categories từ cache hoặc DB"""
    from app import cache_manager

    cache_key = 'categories_active'
    cached = cache_manager.get(cache_key)

    if cached is not None:
        return cached

    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    cache_manager.set(cache_key, categories, timeout=300)  # Cache 5 phút

    return categories


def get_cached_products(category_id=None, featured_only=False, active_only=True):
    """Lấy products từ cache hoặc DB"""
    from app import cache_manager

    # Tạo cache key dựa trên parameters
    if featured_only:
        cache_key = 'products_featured'
    elif category_id:
        cache_key = f'products_cat_{category_id}'
    else:
        cache_key = 'products_all'

    cached = cache_manager.get(cache_key)
    if cached is not None:
        return cached

    # Query products
    query = Product.query

    if active_only:
        query = query.filter_by(is_active=True)

    if featured_only:
        query = query.filter_by(is_featured=True)

    if category_id:
        query = query.filter_by(category_id=category_id)

    # Order by created_at descending
    query = query.order_by(Product.created_at.desc())

    products = query.all()

    # Cache kết quả (5 phút)
    cache_manager.set(cache_key, products, timeout=300)

    return products