from flask import render_template, request, redirect, url_for, send_from_directory, current_app, abort, jsonify
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

    # Mapping trang tĩnh với từ khóa
    static_pages_map = {
        'điều khoản': {
            'title': 'Điều khoản dịch vụ',
            'url': 'main.policy',
            'params': {'policy_slug': 'dieu-khoan-dich-vu'},
            'icon': 'bi-file-earmark-text',
            'description': 'Các quy định và điều khoản khi sử dụng dịch vụ'
        },
        'dịch vụ': {
            'title': 'Điều khoản dịch vụ',
            'url': 'main.policy',
            'params': {'policy_slug': 'dieu-khoan-dich-vu'},
            'icon': 'bi-file-earmark-text',
            'description': 'Các quy định và điều khoản khi sử dụng dịch vụ'
        },
        'chính sách': {
            'title': 'Chính sách',
            'url': 'main.policy',
            'params': {},
            'icon': 'bi-shield-check',
            'description': 'Các chính sách vận chuyển, đổi trả, bảo hành và bảo mật'
        },
        'vận chuyển': {
            'title': 'Chính sách vận chuyển',
            'url': 'main.policy',
            'params': {'policy_slug': 'van-chuyen'},
            'icon': 'bi-truck',
            'description': 'Thông tin về vận chuyển và giao hàng'
        },
        'giao hàng': {
            'title': 'Chính sách vận chuyển',
            'url': 'main.policy',
            'params': {'policy_slug': 'van-chuyen'},
            'icon': 'bi-truck',
            'description': 'Thông tin về vận chuyển và giao hàng'
        },
        'đổi trả': {
            'title': 'Chính sách đổi trả',
            'url': 'main.policy',
            'params': {'policy_slug': 'doi-tra'},
            'icon': 'bi-arrow-repeat',
            'description': 'Quy định về đổi trả sản phẩm'
        },
        'hoàn trả': {
            'title': 'Chính sách đổi trả',
            'url': 'main.policy',
            'params': {'policy_slug': 'doi-tra'},
            'icon': 'bi-arrow-repeat',
            'description': 'Quy định về đổi trả sản phẩm'
        },
        'bảo hành': {
            'title': 'Chính sách bảo hành',
            'url': 'main.policy',
            'params': {'policy_slug': 'bao-hanh'},
            'icon': 'bi-shield-check',
            'description': 'Thông tin về bảo hành sản phẩm'
        },
        'bảo mật': {
            'title': 'Chính sách bảo mật',
            'url': 'main.policy',
            'params': {'policy_slug': 'bao-mat'},
            'icon': 'bi-lock',
            'description': 'Cam kết bảo mật thông tin khách hàng'
        },
        'quyền riêng tư': {
            'title': 'Chính sách bảo mật',
            'url': 'main.policy',
            'params': {'policy_slug': 'bao-mat'},
            'icon': 'bi-lock',
            'description': 'Cam kết bảo mật thông tin khách hàng'
        },
        'giới thiệu': {
            'title': 'Giới thiệu về chúng tôi',
            'url': 'main.about',
            'params': {},
            'icon': 'bi-info-circle',
            'description': 'Thông tin về công ty và đội ngũ'
        },
        'về chúng tôi': {
            'title': 'Giới thiệu về chúng tôi',
            'url': 'main.about',
            'params': {},
            'icon': 'bi-info-circle',
            'description': 'Thông tin về công ty và đội ngũ'
        },
        'công ty': {
            'title': 'Giới thiệu về chúng tôi',
            'url': 'main.about',
            'params': {},
            'icon': 'bi-info-circle',
            'description': 'Thông tin về công ty và đội ngũ'
        },
        'liên hệ': {
            'title': 'Liên hệ',
            'url': 'main.contact',
            'params': {},
            'icon': 'bi-envelope',
            'description': 'Thông tin liên hệ và gửi tin nhắn'
        },
        'hỏi đáp': {
            'title': 'Câu hỏi thường gặp',
            'url': 'main.faq',
            'params': {},
            'icon': 'bi-question-circle',
            'description': 'Các câu hỏi thường gặp và giải đáp'
        },
        'faq': {
            'title': 'Câu hỏi thường gặp',
            'url': 'main.faq',
            'params': {},
            'icon': 'bi-question-circle',
            'description': 'Các câu hỏi thường gặp và giải đáp'
        },
        'câu hỏi': {
            'title': 'Câu hỏi thường gặp',
            'url': 'main.faq',
            'params': {},
            'icon': 'bi-question-circle',
            'description': 'Các câu hỏi thường gặp và giải đáp'
        },
        'màu sắc': {
            'title': 'Bảng màu sản phẩm',
            'url': 'main.color_chart',
            'params': {},
            'icon': 'bi-palette',
            'description': 'Bảng màu và mẫu sản phẩm'
        },
        'bảng màu': {
            'title': 'Bảng màu sản phẩm',
            'url': 'main.color_chart',
            'params': {},
            'icon': 'bi-palette',
            'description': 'Bảng màu và mẫu sản phẩm'
        },
        'hướng dẫn': {
            'title': 'Hướng dẫn thi công',
            'url': 'main.installation_guide',
            'params': {},
            'icon': 'bi-tools',
            'description': 'Hướng dẫn thi công và lắp đặt'
        },
        'thi công': {
            'title': 'Hướng dẫn thi công',
            'url': 'main.installation_guide',
            'params': {},
            'icon': 'bi-tools',
            'description': 'Hướng dẫn thi công và lắp đặt'
        },
        'lắp đặt': {
            'title': 'Hướng dẫn thi công',
            'url': 'main.installation_guide',
            'params': {},
            'icon': 'bi-tools',
            'description': 'Hướng dẫn thi công và lắp đặt'
        },
    }

    # Tìm trang tĩnh phù hợp với fuzzy matching (tránh trùng lặp)
    matched_pages = {}
    keyword_lower = keyword.lower()
    keyword_words = keyword_lower.split()

    for key, page_info in static_pages_map.items():
        # Match nếu:
        # 1. Từ khóa chứa trong key (exact)
        # 2. HOẶC bất kỳ từ nào trong keyword match với key
        # 3. HOẶC key chứa trong từ khóa
        match = False

        if key in keyword_lower:
            match = True
        else:
            # Kiểm tra từng từ trong keyword
            for word in keyword_words:
                if word in key or key in word:
                    match = True
                    break

        if match:
            # Dùng URL làm key để tránh trùng lặp
            page_key = page_info['url'] + str(page_info.get('params', {}))
            if page_key not in matched_pages:
                matched_pages[page_key] = page_info

    # Chuyển về list
    static_pages = list(matched_pages.values())

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
                           blogs=blogs,
                           static_pages=static_pages)


@main_bp.route('/api/search-suggestions')
def search_suggestions():
    """API endpoint trả về gợi ý tìm kiếm cho autocomplete"""
    keyword = request.args.get('q', '').strip()

    # Validate input
    if not keyword or len(keyword) < 2:
        return jsonify({'suggestions': []})

    # Giới hạn keyword length để tránh abuse
    if len(keyword) > 100:
        return jsonify({'suggestions': []})

    # Mapping trang tĩnh (giống như ở trên)
    static_pages_map = {
        'điều khoản': {
            'title': 'Điều khoản dịch vụ',
            'url': '/chinh-sach/dieu-khoan-dich-vu',
            'icon': 'bi-file-earmark-text',
            'type': 'page'
        },
        'dịch vụ': {
            'title': 'Điều khoản dịch vụ',
            'url': '/chinh-sach/dieu-khoan-dich-vu',
            'icon': 'bi-file-earmark-text',
            'type': 'page'
        },
        'chính sách': {
            'title': 'Chính sách',
            'url': '/chinh-sach',
            'icon': 'bi-shield-check',
            'type': 'page'
        },
        'policy': {
            'title': 'Chính sách',
            'url': '/chinh-sach',
            'icon': 'bi-shield-check',
            'type': 'page'
        },
        'vận chuyển': {
            'title': 'Chính sách vận chuyển',
            'url': '/chinh-sach/van-chuyen',
            'icon': 'bi-truck',
            'type': 'page'
        },
        'ship': {
            'title': 'Chính sách vận chuyển',
            'url': '/chinh-sach/van-chuyen',
            'icon': 'bi-truck',
            'type': 'page'
        },
        'giao hàng': {
            'title': 'Chính sách vận chuyển',
            'url': '/chinh-sach/van-chuyen',
            'icon': 'bi-truck',
            'type': 'page'
        },
        'đổi trả': {
            'title': 'Chính sách đổi trả',
            'url': '/chinh-sach/doi-tra',
            'icon': 'bi-arrow-repeat',
            'type': 'page'
        },
        'đổi': {
            'title': 'Chính sách đổi trả',
            'url': '/chinh-sach/doi-tra',
            'icon': 'bi-arrow-repeat',
            'type': 'page'
        },
        'trả': {
            'title': 'Chính sách đổi trả',
            'url': '/chinh-sach/doi-tra',
            'icon': 'bi-arrow-repeat',
            'type': 'page'
        },
        'hoàn trả': {
            'title': 'Chính sách đổi trả',
            'url': '/chinh-sach/doi-tra',
            'icon': 'bi-arrow-repeat',
            'type': 'page'
        },
        'bảo hành': {
            'title': 'Chính sách bảo hành',
            'url': '/chinh-sach/bao-hanh',
            'icon': 'bi-shield-check',
            'type': 'page'
        },
        'bảo': {
            'title': 'Chính sách bảo hành',
            'url': '/chinh-sach/bao-hanh',
            'icon': 'bi-shield-check',
            'type': 'page'
        },
        'hành': {
            'title': 'Chính sách bảo hành',
            'url': '/chinh-sach/bao-hanh',
            'icon': 'bi-shield-check',
            'type': 'page'
        },
        'bảo mật': {
            'title': 'Chính sách bảo mật',
            'url': '/chinh-sach/bao-mat',
            'icon': 'bi-lock',
            'type': 'page'
        },
        'mật': {
            'title': 'Chính sách bảo mật',
            'url': '/chinh-sach/bao-mat',
            'icon': 'bi-lock',
            'type': 'page'
        },
        'quyền riêng tư': {
            'title': 'Chính sách bảo mật',
            'url': '/chinh-sach/bao-mat',
            'icon': 'bi-lock',
            'type': 'page'
        },
        'privacy': {
            'title': 'Chính sách bảo mật',
            'url': '/chinh-sach/bao-mat',
            'icon': 'bi-lock',
            'type': 'page'
        },
        'giới thiệu': {
            'title': 'Giới thiệu',
            'url': '/gioi-thieu',
            'icon': 'bi-info-circle',
            'type': 'page'
        },
        'về chúng tôi': {
            'title': 'Giới thiệu',
            'url': '/gioi-thieu',
            'icon': 'bi-info-circle',
            'type': 'page'
        },
        'about': {
            'title': 'Giới thiệu',
            'url': '/gioi-thieu',
            'icon': 'bi-info-circle',
            'type': 'page'
        },
        'công ty': {
            'title': 'Giới thiệu',
            'url': '/gioi-thieu',
            'icon': 'bi-info-circle',
            'type': 'page'
        },
        'liên hệ': {
            'title': 'Liên hệ',
            'url': '/lien-he',
            'icon': 'bi-envelope',
            'type': 'page'
        },
        'contact': {
            'title': 'Liên hệ',
            'url': '/lien-he',
            'icon': 'bi-envelope',
            'type': 'page'
        },
        'hỏi đáp': {
            'title': 'Câu hỏi thường gặp',
            'url': '/hoi-dap',
            'icon': 'bi-question-circle',
            'type': 'page'
        },
        'faq': {
            'title': 'Câu hỏi thường gặp',
            'url': '/hoi-dap',
            'icon': 'bi-question-circle',
            'type': 'page'
        },
        'hỏi': {
            'title': 'Câu hỏi thường gặp',
            'url': '/hoi-dap',
            'icon': 'bi-question-circle',
            'type': 'page'
        },
        'câu hỏi': {
            'title': 'Câu hỏi thường gặp',
            'url': '/hoi-dap',
            'icon': 'bi-question-circle',
            'type': 'page'
        },
        'màu sắc': {
            'title': 'Bảng màu',
            'url': '/bang-mau',
            'icon': 'bi-palette',
            'type': 'page'
        },
        'màu': {
            'title': 'Bảng màu',
            'url': '/bang-mau',
            'icon': 'bi-palette',
            'type': 'page'
        },
        'bảng màu': {
            'title': 'Bảng màu',
            'url': '/bang-mau',
            'icon': 'bi-palette',
            'type': 'page'
        },
        'bảng': {
            'title': 'Bảng màu',
            'url': '/bang-mau',
            'icon': 'bi-palette',
            'type': 'page'
        },
        'color': {
            'title': 'Bảng màu',
            'url': '/bang-mau',
            'icon': 'bi-palette',
            'type': 'page'
        },
        'hướng dẫn': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
        'hướng': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
        'dẫn': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
        'thi công': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
        'lắp đặt': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
        'guide': {
            'title': 'Hướng dẫn thi công',
            'url': '/huong-dan-thi-cong',
            'icon': 'bi-tools',
            'type': 'page'
        },
    }

    suggestions = []
    keyword_lower = keyword.lower()

    # Tìm trang tĩnh với fuzzy matching (tránh duplicate)
    matched_pages = {}

    # Tách keyword thành các từ riêng lẻ để tìm kiếm thông minh hơn
    keyword_words = keyword_lower.split()

    for key, page_info in static_pages_map.items():
        # Match nếu:
        # 1. Từ khóa chứa trong key (exact)
        # 2. HOẶC bất kỳ từ nào trong keyword match với key
        # 3. HOẶC key chứa trong từ khóa
        match = False

        if key in keyword_lower:
            match = True
        else:
            # Kiểm tra từng từ trong keyword
            for word in keyword_words:
                if word in key or key in word:
                    match = True
                    break

        if match:
            page_key = page_info['url']
            if page_key not in matched_pages:
                matched_pages[page_key] = page_info

    suggestions.extend(list(matched_pages.values()))

    # Tìm sản phẩm (top 5)
    try:
        products = Product.query.filter(
            Product.name.ilike(f'%{keyword}%'),
            Product.is_active == True
        ).limit(5).all()

        for product in products:
            suggestions.append({
                'title': product.name,
                'url': f'/san-pham/{product.slug}',
                'icon': 'bi-box-seam',
                'type': 'product',
                'image': product.image if hasattr(product, 'image') else None
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching products: {e}")

    # Tìm blog (top 3)
    try:
        blogs = Blog.query.filter(
            or_(
                Blog.title.ilike(f'%{keyword}%'),
                Blog.excerpt.ilike(f'%{keyword}%')
            ),
            Blog.is_active == True
        ).limit(3).all()

        for blog in blogs:
            suggestions.append({
                'title': blog.title,
                'url': f'/tin-tuc/{blog.slug}',
                'icon': 'bi-journal-text',
                'type': 'blog'
            })
    except Exception as e:
        current_app.logger.error(f"Error fetching blogs: {e}")

    # Giới hạn 10 kết quả
    return jsonify({'suggestions': suggestions[:10]})


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