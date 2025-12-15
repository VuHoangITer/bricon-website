# File: app/admin/routes/products.py
"""
🛍️ Products Management Routes (Admin) - JSON Dynamic Version
"""

from flask import render_template, request, flash, redirect, url_for
from app import db, cache_manager
from app.models.product import Product, get_cached_products
from app.forms.product import ProductForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.helpers import get_image_from_form
from app.models.features import feature_required

# ⭐ IMPORT HELPER
from app.admin.utils.technical_parser import (
    parse_technical_info,
    technical_info_to_text,
    validate_technical_info
)


# ==================== DANH SÁCH SẢN PHẨM ====================
@admin_bp.route('/products')
@permission_required('view_products')
@feature_required('products')
def products():
    """Danh sách sản phẩm"""
    page = request.args.get('page', 1, type=int)

    cache_key = 'admin_products_all'
    products_list = cache_manager.get(cache_key)

    if products_list is None:
        products_list = Product.query.order_by(Product.created_at.desc()).all()
        cache_manager.set(cache_key, products_list)

    # Phân trang
    per_page = 20
    total = len(products_list)
    start = (page - 1) * per_page
    end = start + per_page
    products_page = products_list[start:end]

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
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (self.page - left_current <= num <= self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    pagination = SimplePagination(products_page, page, per_page, total)
    return render_template('admin/san_pham/products.html', products=pagination)


# ==================== THÊM SẢN PHẨM ====================
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@permission_required('manage_products')
@feature_required('products')
def add_product():
    """Thêm sản phẩm mới"""
    form = ProductForm()

    if form.validate_on_submit():
        # Validate technical info
        if form.technical_info_raw.data:
            is_valid, message = validate_technical_info(form.technical_info_raw.data)
            if not is_valid:
                flash(f'❌ Lỗi định dạng:\n{message}', 'danger')
                return render_template('admin/san_pham/product_form.html',
                                     form=form, title='Thêm sản phẩm')

        # Xử lý hình ảnh
        image_path = get_image_from_form(form.image, 'image', folder='products')

        # Tạo sản phẩm
        product = Product(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            price=form.price.data,
            old_price=form.old_price.data,
            category_id=form.category_id.data,
            image=image_path,
            is_featured=form.is_featured.data,
            is_active=form.is_active.data
        )

        # ⭐ XỬ LÝ THÔNG TIN KỸ THUẬT
        if form.technical_info_raw.data:
            product.technical_info = parse_technical_info(form.technical_info_raw.data)

        # Lưu
        try:
            db.session.add(product)
            db.session.commit()
            flash(f'✅ Đã thêm sản phẩm "{product.name}"!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/san_pham/product_form.html',
                          form=form, title='Thêm sản phẩm')


# ==================== SỬA SẢN PHẨM ====================
@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_products')
@feature_required('products')
def edit_product(id):
    """Sửa sản phẩm"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        # Validate
        if form.technical_info_raw.data:
            is_valid, message = validate_technical_info(form.technical_info_raw.data)
            if not is_valid:
                flash(f'❌ Lỗi định dạng:\n{message}', 'danger')
                return render_template('admin/san_pham/product_form.html',
                                     form=form,
                                     title=f'Sửa: {product.name}',
                                     product=product)

        # Xử lý hình ảnh
        new_image = get_image_from_form(form.image, 'image', folder='products')
        if new_image:
            product.image = new_image

        # Cập nhật thông tin
        product.name = form.name.data
        product.slug = form.slug.data
        product.description = form.description.data
        product.price = form.price.data
        product.old_price = form.old_price.data
        product.category_id = form.category_id.data
        product.is_featured = form.is_featured.data
        product.is_active = form.is_active.data

        # ⭐ CẬP NHẬT THÔNG TIN KỸ THUẬT
        if form.technical_info_raw.data:
            product.technical_info = parse_technical_info(form.technical_info_raw.data)
        else:
            product.technical_info = None

        # Lưu
        try:
            db.session.commit()
            flash(f'✅ Đã cập nhật "{product.name}"!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    # ⭐ LOAD DỮ LIỆU KHI EDIT
    if request.method == 'GET':
        if product.technical_info:
            form.technical_info_raw.data = technical_info_to_text(product.technical_info)

    return render_template('admin/san_pham/product_form.html',
                          form=form,
                          title=f'Sửa: {product.name}',
                          product=product)


# ==================== XÓA SẢN PHẨM ====================
@admin_bp.route('/products/delete/<int:id>')
@permission_required('manage_products')
@feature_required('products')
def delete_product(id):
    """Xóa sản phẩm"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('✅ Đã xóa sản phẩm!', 'success')
    return redirect(url_for('admin.products'))