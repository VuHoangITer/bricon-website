from flask import render_template, request, redirect, url_for, flash
from app.main import main_bp
from app import db, cache_manager
from app.models.product import Product, Category, get_cached_products
from app.models.settings import get_setting
from sqlalchemy.orm import joinedload
from jinja2 import Template
from datetime import datetime, timedelta
from app.models.features import feature_required

@main_bp.route('/san-pham')
@main_bp.route('/loai-san-pham/<category_slug>')
@feature_required('products')
def products(category_slug=None):
    """Trang danh sách sản phẩm với cache thông minh"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'latest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # ========== XỬ LÝ BACKWARD COMPATIBILITY ==========
    old_category_id = request.args.get('category', type=int)
    if old_category_id:
        category = Category.query.get(old_category_id)
        if category and category.is_active:
            return redirect(url_for('main.products',
                                    category_slug=category.slug,
                                    search=search if search else None,
                                    sort=sort if sort != 'latest' else None,
                                    page=page if page > 1 else None),
                            code=301)
        elif not category:
            flash('Danh mục không tồn tại.', 'warning')
            return redirect(url_for('main.products'))

    # ========== LẤY PRODUCTS TỪ CACHE ==========
    current_category = None
    category_id = None

    # Xác định category nếu có
    if category_slug:
        current_category = Category.query.filter_by(
            slug=category_slug,
            is_active=True
        ).first_or_404()
        category_id = current_category.id

    if search:
        query = Product.query.options(joinedload(Product.category)).filter_by(is_active=True)
        if category_id:
            query = query.filter_by(category_id=category_id)
        query = query.filter(Product.name.ilike(f'%{search}%'))
        products_list = query.all()
    else:
        products_list = get_cached_products(category_id=category_id, featured_only=False)

    # ========== LỌC THEO GIÁ ==========
    if min_price is not None or max_price is not None:
        filtered_products = []
        for p in products_list:
            if p.price is None:
                continue
            if min_price is not None and p.price < min_price:
                continue
            if max_price is not None and p.price > max_price:
                continue
            filtered_products.append(p)
        products_list = filtered_products

    # ========== SẮP XẾP (TRONG MEMORY) ==========
    if sort == 'latest':
        products_list = sorted(products_list, key=lambda p: p.created_at, reverse=True)
    elif sort == 'price_asc':
        products_list = sorted(products_list, key=lambda p: p.price or 0)
    elif sort == 'price_desc':
        products_list = sorted(products_list, key=lambda p: p.price or 0, reverse=True)
    elif sort == 'popular':
        products_list = sorted(products_list, key=lambda p: p.views, reverse=True)

    # ========== PHÂN TRANG THỦ CÔNG ==========
    per_page = 6
    total = len(products_list)
    total_pages = (total + per_page - 1) // per_page  # Làm tròn lên

    # Slice products cho trang hiện tại
    start = (page - 1) * per_page
    end = start + per_page
    products = products_list[start:end]

    # Tạo pagination object giả (để template không bị lỗi)
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None

        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            """Generate page numbers for pagination"""
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (self.page - left_current <= num <= self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    pagination = SimplePagination(products, page, per_page, total)

    # ✅ LẤY CATEGORIES TỪ CACHE (đã có sẵn trong context_processor)
    categories = Category.query.filter_by(is_active=True).all()

    return render_template('public/san_pham/products.html',
                           products=products,
                           categories=categories,
                           pagination=pagination,
                           current_category=current_category,
                           current_search=search,
                           current_sort=sort,
                           min_price=min_price,
                           max_price=max_price)


@main_bp.route('/san-pham/<slug>')
@feature_required('products')
def product_detail(slug):
    """
    Trang chi tiết sản phẩm - KHÔNG CACHE
    (Vì cần tăng views realtime)
    """
    product = Product.query.options(joinedload(Product.category)) \
        .filter_by(slug=slug, is_active=True).first_or_404()

    # Tăng lượt xem
    product.views += 1
    db.session.commit()

    # ✅ LẤY RELATED PRODUCTS TỪ CACHE
    cache_key = f'related_products_{product.category_id}_{product.id}'
    related_products = cache_manager.get(cache_key)

    if related_products is None:
        related_products = Product.query.options(joinedload(Product.category)) \
            .filter(
                Product.category_id == product.category_id,
                Product.id != product.id,
                Product.is_active == True
            ).limit(4).all()
        cache_manager.set(cache_key, related_products)
    else:
        pass

    # ========== RENDER META DESCRIPTION ĐỘNG ==========
    rendered_meta_description = None
    meta_template = get_setting('product_meta_description', '')

    if meta_template and ('{{' in meta_template or '{%' in meta_template):
        try:
            template = Template(meta_template)
            rendered_meta_description = template.render(
                product=product,
                get_setting=get_setting
            )
        except Exception as e:
            rendered_meta_description = meta_template.replace('{{ product.name }}', product.name or '')
            rendered_meta_description = rendered_meta_description.replace(
                '{{ get_setting(\'website_name\') }}',
                get_setting('website_name'))
    elif meta_template:
        rendered_meta_description = meta_template
    else:
        rendered_meta_description = f"Mua {product.name} chất lượng cao từ {get_setting('website_name')} với giá tốt nhất."

    return render_template('public/san_pham/product_detail.html',
                           product=product,
                           related_products=related_products,
                           rendered_meta_description=rendered_meta_description,
                           now=datetime.now(),
                           timedelta=timedelta)