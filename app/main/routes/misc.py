from flask import render_template, request, redirect, url_for, send_from_directory, current_app, abort
from app.main import main_bp
from app.models.product import Product
from app.models.content import Blog
from sqlalchemy import or_
import os


@main_bp.route('/tim-kiem')
def search():
    """Trang tìm kiếm tổng hợp"""
    keyword = request.args.get('q', '')

    if not keyword:
        return redirect(url_for('main.index'))

    # Tìm sản phẩm
    products = Product.query.filter(
        Product.name.ilike(f'%{keyword}%'),
        Product.is_active == True
    ).limit(10).all()

    # Tìm blog
    blogs = Blog.query.filter(
        or_(
            Blog.title.ilike(f'%{keyword}%'),
            Blog.excerpt.ilike(f'%{keyword}%')
        ),
        Blog.is_active == True
    ).limit(5).all()

    return render_template('public/search.html',
                           keyword=keyword,
                           products=products,
                           blogs=blogs)


# Route cũ redirect sang mới
@main_bp.route('/search')
def old_search():
    """Redirect URL cũ sang URL mới"""
    keyword = request.args.get('q', '')
    return redirect(url_for('main.search', q=keyword), code=301)


@main_bp.route('/sitemap.xml')
def sitemap():
    """Phục vụ file sitemap.xml"""
    sitemap_path = os.path.join(current_app.static_folder, 'sitemap.xml')
    if os.path.exists(sitemap_path):
        return send_from_directory(current_app.static_folder, 'sitemap.xml', mimetype='application/xml')
    else:
        abort(404, description="Sitemap not found")


@main_bp.route('/robots.txt')
def robots_txt():
    """Phục vụ file robots.txt"""
    robots_path = os.path.join(current_app.static_folder, 'robots.txt')
    if os.path.exists(robots_path):
        return send_from_directory(current_app.static_folder, 'robots.txt', mimetype='text/plain')
    else:
        abort(404, description="Robots.txt not found")