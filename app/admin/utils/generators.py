"""
🤖 SEO File Generators
Tạo sitemap.xml và robots.txt động
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import url_for, current_app, request
from app.models import Product, Blog, Project, get_setting


def generate_sitemap():
    """
    📄 Tạo sitemap.xml động dựa trên database

    Bao gồm:
    - Trang chủ
    - Trang tĩnh (about, products, contact, ...)
    - Products
    - Blogs
    - Projects
    """

    sitemap = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Trang chính
    url = ET.SubElement(sitemap, 'url')
    ET.SubElement(url, 'loc').text = get_setting('main_url', request.url_root)
    ET.SubElement(url, 'lastmod').text = datetime.utcnow().strftime('%Y-%m-%d')
    ET.SubElement(url, 'changefreq').text = 'daily'
    ET.SubElement(url, 'priority').text = '1.0'

    # Trang tĩnh
    static_pages = [
        ('about', 'weekly', '0.8'),
        ('products', 'daily', '0.9'),
        ('contact', 'weekly', '0.7'),
        ('policy', 'monthly', '0.6'),
        ('faq', 'weekly', '0.7'),
        ('careers', 'weekly', '0.7'),
        ('projects', 'weekly', '0.8'),
    ]
    for page, freq, priority in static_pages:
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = url_for('main.' + page, _external=True)
        ET.SubElement(url, 'lastmod').text = datetime.utcnow().strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = freq
        ET.SubElement(url, 'priority').text = priority

    # Sản phẩm
    products = Product.query.filter_by(is_active=True).all()
    for product in products:
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = url_for('main.product_detail', slug=product.slug, _external=True)
        ET.SubElement(url, 'lastmod').text = product.updated_at.strftime(
            '%Y-%m-%d') if product.updated_at else datetime.utcnow().strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.8'

    # Blog
    blogs = Blog.query.filter_by(is_active=True).all()
    for blog in blogs:
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = url_for('main.blog_detail', slug=blog.slug, _external=True)
        ET.SubElement(url, 'lastmod').text = blog.updated_at.strftime(
            '%Y-%m-%d') if blog.updated_at else datetime.utcnow().strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.7'

    # Dự án
    projects = Project.query.filter_by(is_active=True).all()
    for project in projects:
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = url_for('main.project_detail', slug=project.slug, _external=True)
        ET.SubElement(url, 'lastmod').text = project.updated_at.strftime(
            '%Y-%m-%d') if project.updated_at else datetime.utcnow().strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.8'

    # Ghi file sitemap.xml
    sitemap_path = os.path.join(current_app.static_folder, 'sitemap.xml')
    tree = ET.ElementTree(sitemap)
    tree.write(sitemap_path)


def generate_robots_txt():
    """
    🤖 Tạo robots.txt với sitemap URL
    """

    robots_content = f"""
    User-agent: *
    Disallow: /admin/
    Allow: /

    Sitemap: {get_setting('main_url', request.url_root)}sitemap.xml
    """
    robots_path = os.path.join(current_app.static_folder, 'robots.txt')
    with open(robots_path, 'w') as f:
        f.write(robots_content)
