# File: app/admin/routes/products.py
"""
🛍️ Products Management Routes (Admin) - JSON Dynamic Version
"""

from flask import render_template, request, flash, redirect, url_for
from app import db, cache_manager
from app.models.product import Product
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
    """Danh sách sản phẩm với cache được fix"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # ✅ QUERY TRỰC TIẾP TỪ DATABASE - KHÔNG DÙNG CACHE
    # Cache có thể gây vấn đề với pagination và real-time updates
    query = Product.query.order_by(Product.created_at.desc())

    # Sử dụng paginate của SQLAlchemy
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

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

            # ✅ CLEAR CACHE SAU KHI THÊM
            cache_manager.clear('products')

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

            # ✅ CLEAR CACHE SAU KHI SỬA
            cache_manager.clear('products')

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

    try:
        db.session.delete(product)
        db.session.commit()

        # ✅ CLEAR CACHE SAU KHI XÓA
        cache_manager.clear('products')

        flash('✅ Đã xóa sản phẩm!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Lỗi khi xóa: {str(e)}', 'danger')

    return redirect(url_for('admin.products'))