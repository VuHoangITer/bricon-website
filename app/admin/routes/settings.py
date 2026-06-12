"""
⚙️ System Settings Routes
- General settings (website name, email, hotline, ...)
- Theme settings (logo, colors, ...)
- SEO settings (meta tags, favicon, sitemap, ...)
- Contact & Social settings
- Integration settings (Cloudinary, Gemini, GA, ...)
- Cache Management

🔒 Permission: manage_settings

📝 Note: Tạo sitemap.xml và robots.txt sau khi save
"""

from flask import render_template, request, flash, redirect, url_for, jsonify
from app import db, cache_manager
from app.models.settings import get_setting, set_setting
from app.forms.settings import SettingsForm
from app.utils import save_upload_file
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.generators import generate_sitemap, generate_robots_txt

@admin_bp.route('/settings', methods=['GET', 'POST'])
@permission_required('manage_settings')
def settings():
    """Quản lý cài đặt hệ thống"""
    form = SettingsForm()

    if form.validate_on_submit():
        # ==================== GENERAL SETTINGS ====================
        set_setting('website_name', form.website_name.data, 'general', 'Tên website')
        set_setting('slogan', form.slogan.data, 'general', 'Slogan của website')
        set_setting('address', form.address.data, 'general', 'Địa chỉ công ty')
        set_setting('email', form.email.data, 'general', 'Email chính')
        set_setting('hotline', form.hotline.data, 'general', 'Số hotline')
        set_setting('main_url', form.main_url.data, 'general', 'URL chính của website')
        set_setting('company_info', form.company_info.data, 'general', 'Thông tin công ty')

        # ==================== THEME/UI SETTINGS ====================
        if form.logo.data:
            logo_path = save_upload_file(form.logo.data, 'logos')
            if isinstance(logo_path, tuple):
                logo_path = logo_path[0]
            set_setting('logo_url', logo_path, 'theme', 'URL logo website')

        if form.logo_chatbot.data:
            chatbot_logo_path = save_upload_file(form.logo_chatbot.data, 'logos')
            if isinstance(chatbot_logo_path, tuple):
                chatbot_logo_path = chatbot_logo_path[0]
            set_setting('logo_chatbot_url', chatbot_logo_path, 'theme', 'URL logo chatbot')

        # ==================== SEO & META DEFAULTS ====================
        set_setting('meta_title', form.meta_title.data, 'seo', 'Meta title mặc định')
        set_setting('meta_description', form.meta_description.data, 'seo', 'Meta description mặc định')
        set_setting('meta_keywords', form.meta_keywords.data, 'seo', 'Meta keywords mặc định')

        # Favicon uploads
        if form.favicon_ico.data:
            favicon_ico_path = save_upload_file(form.favicon_ico.data, 'favicons')
            if isinstance(favicon_ico_path, tuple):
                favicon_ico_path = favicon_ico_path[0]
            set_setting('favicon_ico_url', favicon_ico_path, 'seo', 'Favicon .ico')

        if form.favicon_png.data:
            favicon_png_path = save_upload_file(form.favicon_png.data, 'favicons')
            if isinstance(favicon_png_path, tuple):
                favicon_png_path = favicon_png_path[0]
            set_setting('favicon_png_url', favicon_png_path, 'seo', 'Favicon PNG 96x96')

        if form.favicon_svg.data:
            favicon_svg_path = save_upload_file(form.favicon_svg.data, 'favicons')
            if isinstance(favicon_svg_path, tuple):
                favicon_svg_path = favicon_svg_path[0]
            set_setting('favicon_svg_url', favicon_svg_path, 'seo', 'Favicon SVG')

        if form.apple_touch_icon.data:
            apple_icon_path = save_upload_file(form.apple_touch_icon.data, 'favicons')
            if isinstance(apple_icon_path, tuple):
                apple_icon_path = apple_icon_path[0]
            set_setting('apple_touch_icon_url', apple_icon_path, 'seo', 'Apple Touch Icon')

        if form.favicon.data:
            favicon_path = save_upload_file(form.favicon.data, 'favicons')
            if isinstance(favicon_path, tuple):
                favicon_path = favicon_path[0]
            set_setting('favicon_url', favicon_path, 'seo', 'URL favicon')

        if form.default_share_image.data:
            share_image_path = save_upload_file(form.default_share_image.data, 'share_images')
            if isinstance(share_image_path, tuple):
                share_image_path = share_image_path[0]
            set_setting('default_share_image', share_image_path, 'seo', 'Ảnh chia sẻ mặc định')

        # Open Graph settings
        set_setting('og_title', form.meta_title.data, 'seo', 'OG title mặc định')
        set_setting('og_description', form.meta_description.data, 'seo', 'OG description mặc định')
        set_setting('og_image', get_setting('default_share_image', ''), 'seo', 'OG image mặc định')

        # Page-specific meta descriptions
        set_setting('index_meta_description', form.index_meta_description.data, 'seo', 'Meta description trang chủ')
        set_setting('about_meta_description', form.about_meta_description.data, 'seo', 'Meta description trang giới thiệu')
        set_setting('contact_meta_description', form.contact_meta_description.data, 'seo', 'Meta description trang liên hệ')
        set_setting('products_meta_description', form.products_meta_description.data, 'seo', 'Meta description trang sản phẩm')
        set_setting('blog_meta_description', form.blog_meta_description.data, 'seo', 'Meta description trang blog')
        set_setting('careers_meta_description', form.careers_meta_description.data, 'seo', 'Meta description trang tuyển dụng')
        set_setting('faq_meta_description', form.faq_meta_description.data, 'seo', 'Meta description trang FAQ')
        set_setting('projects_meta_description', form.projects_meta_description.data, 'seo', 'Meta description trang dự án')

        # ==================== CONTACT & SOCIAL SETTINGS ====================
        set_setting('contact_email', form.contact_email.data, 'contact', 'Email liên hệ')
        set_setting('facebook_url', form.facebook_url.data, 'contact', 'URL Facebook')
        set_setting('facebook_messenger_url', form.facebook_messenger_url.data, 'contact', 'Facebook Messenger URL')
        set_setting('zalo_url', form.zalo_url.data, 'contact', 'URL Zalo')
        set_setting('shopee_url', form.shopee_url.data, 'contact', 'URL Shopee')
        set_setting('tiktok_url', form.tiktok_url.data, 'contact', 'URL TikTok')
        set_setting('youtube_url', form.youtube_url.data, 'contact', 'URL YouTube')
        set_setting('google_maps', form.google_maps.data, 'contact', 'Mã nhúng Google Maps')
        set_setting('working_hours', form.working_hours.data, 'contact', 'Giờ làm việc')
        set_setting('branch_addresses', form.branch_addresses.data, 'contact', 'Danh sách địa chỉ chi nhánh')

        # ==================== SYSTEM & SECURITY SETTINGS ====================
        set_setting('login_attempt_limit', str(form.login_attempt_limit.data), 'system', 'Giới hạn đăng nhập sai')

        # ✅ LƯU CACHE TIME VÀ CLEAR CACHE
        old_cache_time = get_setting('cache_time', '300')
        new_cache_time = str(form.cache_time.data)
        set_setting('cache_time', new_cache_time, 'system', 'Thời gian cache (giây)')

        # Nếu thay đổi cache time, clear toàn bộ cache
        if old_cache_time != new_cache_time:
            cache_manager.clear()
            flash(f'⚙️ Cache time đã thay đổi từ {old_cache_time}s → {new_cache_time}s. Cache đã được xóa.', 'info')

        # ==================== INTEGRATION SETTINGS ====================
        set_setting('cloudinary_api_key', form.cloudinary_api_key.data, 'integration', 'API Key Cloudinary')
        set_setting('gemini_api_key', form.gemini_api_key.data, 'integration', 'API Key Gemini/OpenAI')
        set_setting('google_analytics', form.google_analytics.data, 'integration', 'Google Analytics ID')
        set_setting('shopee_api', form.shopee_api.data, 'integration', 'Shopee Integration')
        set_setting('tiktok_api', form.tiktok_api.data, 'integration', 'TikTok Integration')
        set_setting('zalo_oa', form.zalo_oa.data, 'integration', 'Zalo OA')

        # ==================== CONTENT DEFAULTS ====================
        set_setting('terms_of_service', form.terms_of_service.data, 'content', 'Điều khoản dịch vụ')
        set_setting('shipping_policy', form.shipping_policy.data, 'content', 'Chính sách vận chuyển')
        set_setting('return_policy', form.return_policy.data, 'content', 'Chính sách đổi trả')
        set_setting('warranty_policy', form.warranty_policy.data, 'content', 'Chính sách bảo hành')
        set_setting('privacy_policy', form.privacy_policy.data, 'content', 'Chính sách bảo mật')

        # ==================== GENERATE SEO FILES ====================
        try:
            generate_sitemap()
            generate_robots_txt()
        except Exception as e:
            flash(f'Cảnh báo: Không thể tạo sitemap/robots.txt - {str(e)}', 'warning')

        # ✅ CLEAR CACHE SAU KHI SAVE SETTINGS
        cache_manager.clear()

        flash('✅ Cài đặt đã được lưu thành công! Cache đã được xóa.', 'success')

        # Load lại preview images
        form.logo_url = get_setting('logo_url', '')
        form.logo_chatbot_url = get_setting('logo_chatbot_url', '')
        form.favicon_ico_url = get_setting('favicon_ico_url', '')
        form.favicon_png_url = get_setting('favicon_png_url', '')
        form.favicon_svg_url = get_setting('favicon_svg_url', '')
        form.apple_touch_icon_url = get_setting('apple_touch_icon_url', '')
        form.favicon_url = get_setting('favicon_url', '/static/img/favicon.ico')
        form.default_share_image_url = get_setting('default_share_image', '/static/img/default-share.jpg')

    # ==================== LOAD DỮ LIỆU VÀO FORM ====================
    # General Settings
    form.website_name.data = get_setting('website_name', 'Hoangvn')
    form.slogan.data = get_setting('slogan', '')
    form.address.data = get_setting('address', '982/l98/a1 Tân Bình, Tân Phú Nhà Bè')
    form.email.data = get_setting('email', 'info@hoang.vn')
    form.hotline.data = get_setting('hotline', '098.422.6602')
    form.main_url.data = get_setting('main_url', request.url_root)
    form.company_info.data = get_setting('company_info', 'Chúng tôi là công ty hàng đầu trong lĩnh vực thương mại điện tử.')

    # Theme/UI Settings
    form.logo_url = get_setting('logo_url', '')
    form.logo_chatbot_url = get_setting('logo_chatbot_url', '')

    # SEO & Meta Defaults
    form.meta_title.data = get_setting('meta_title', 'Hoangvn - Website doanh nghiệp chuyên nghiệp')
    form.meta_description.data = get_setting('meta_description', 'Website doanh nghiệp chuyên nghiệp cung cấp sản phẩm và dịch vụ chất lượng cao.')
    form.meta_keywords.data = get_setting('meta_keywords', 'thiết kế web, hoangvn, thương mại điện tử')

    # SEO Images
    form.favicon_ico_url = get_setting('favicon_ico_url', '/static/img/favicon.ico')
    form.favicon_png_url = get_setting('favicon_png_url', '/static/img/favicon-96x96.png')
    form.favicon_svg_url = get_setting('favicon_svg_url', '/static/img/favicon.svg')
    form.apple_touch_icon_url = get_setting('apple_touch_icon_url', '/static/img/apple-touch-icon.png')
    form.favicon_url = get_setting('favicon_url', '/static/img/favicon.ico')
    form.default_share_image_url = get_setting('default_share_image', '/static/img/default-share.jpg')

    # Page-specific meta descriptions
    form.index_meta_description.data = get_setting('index_meta_description', 'Khám phá các sản phẩm và dịch vụ chất lượng cao từ Hoangvn.')
    form.about_meta_description.data = get_setting('about_meta_description', 'Giới thiệu về Hoangvn - Công ty hàng đầu trong thương mại điện tử.')
    form.contact_meta_description.data = get_setting('contact_meta_description', 'Liên hệ với Hoangvn để được tư vấn và hỗ trợ nhanh chóng.')
    form.products_meta_description.data = get_setting('products_meta_description', 'Khám phá danh sách sản phẩm chất lượng cao từ Hoangvn.')
    form.blog_meta_description.data = get_setting('blog_meta_description', 'Tin tức và kiến thức hữu ích từ Hoangvn.')
    form.careers_meta_description.data = get_setting('careers_meta_description', 'Cơ hội nghề nghiệp tại Hoangvn với môi trường làm việc chuyên nghiệp.')
    form.faq_meta_description.data = get_setting('faq_meta_description', 'Câu hỏi thường gặp về sản phẩm và dịch vụ của Hoangvn.')
    form.projects_meta_description.data = get_setting('projects_meta_description', 'Các dự án tiêu biểu đã được Hoangvn thực hiện thành công.')

    # Contact & Social Settings
    form.contact_email.data = get_setting('contact_email', 'contact@example.com')
    form.facebook_url.data = get_setting('facebook_url', '')
    form.facebook_messenger_url.data = get_setting('facebook_messenger_url', '')
    form.zalo_url.data = get_setting('zalo_url', '')
    form.shopee_url.data = get_setting('shopee_url', '')
    form.tiktok_url.data = get_setting('tiktok_url', '')
    form.youtube_url.data = get_setting('youtube_url', '')
    form.google_maps.data = get_setting('google_maps', '')
    form.working_hours.data = get_setting('working_hours', '8h - 17h30 (Thứ 2 - Thứ 7)')
    form.branch_addresses.data = get_setting('branch_addresses', '982/l98/a1 Tân Bình, Tân Phú, Nhà Bè\n123 Đường ABC, Quận 1, TP.HCM\n456 Đường XYZ, Quận 3, TP.HCM')

    # System & Security Settings
    form.login_attempt_limit.data = int(get_setting('login_attempt_limit', '5'))
    form.cache_time.data = int(get_setting('cache_time', '300'))

    # Integration Settings
    form.cloudinary_api_key.data = get_setting('cloudinary_api_key', '')
    form.gemini_api_key.data = get_setting('gemini_api_key', '')
    form.google_analytics.data = get_setting('google_analytics', '')
    form.shopee_api.data = get_setting('shopee_api', '')
    form.tiktok_api.data = get_setting('tiktok_api', '')
    form.zalo_oa.data = get_setting('zalo_oa', '')

    # Content Defaults
    form.terms_of_service.data = get_setting('terms_of_service', '')
    form.shipping_policy.data = get_setting('shipping_policy', '')
    form.return_policy.data = get_setting('return_policy', '')
    form.warranty_policy.data = get_setting('warranty_policy', '')
    form.privacy_policy.data = get_setting('privacy_policy', '')

    # ✅ LẤY CACHE STATS
    cache_stats = cache_manager.get_stats()

    return render_template('admin/cai_dat/settings.html', form=form, cache_stats=cache_stats)


# ==================== CACHE API ENDPOINTS ====================

@admin_bp.route('/settings/cache/clear', methods=['POST'])
@permission_required('manage_settings')
def clear_cache():
    """API endpoint để clear cache"""
    pattern = request.json.get('pattern') if request.is_json else None
    cache_manager.clear(pattern)

    return jsonify({
        'success': True,
        'message': f'Cache {"(" + pattern + ")" if pattern else ""} đã được xóa!',
        'stats': cache_manager.get_stats()
    })


@admin_bp.route('/settings/cache/stats', methods=['GET'])
@permission_required('manage_settings')
def cache_stats_api():
    """API endpoint để lấy cache stats"""
    return jsonify({
        'success': True,
        'stats': cache_manager.get_stats()
    })


@admin_bp.route('/test-cache')
@permission_required('manage_settings')
def test_cache():
    """Test xem cache có hoạt động không"""
    from app import cache_manager
    from app.models.product import Category

    # Test 1: Set cache
    cache_manager.set('test_key', 'Hello Cache!')

    # Test 2: Get cache
    value = cache_manager.get('test_key')

    # Test 3: Categories
    cached_cats = cache_manager.get('categories_active')
    if cached_cats is None:
        cats = Category.query.filter_by(is_active=True).all()
        cache_manager.set('categories_active', cats)
        cached_cats = cats
        status = "CACHE MISS - Đã set cache mới"
    else:
        status = "CACHE HIT - Lấy từ cache"

    stats = cache_manager.get_stats()

    return f"""
    <h1>Cache Test Results</h1>
    <p>Test Key: {value}</p>
    <p>Categories Status: {status}</p>
    <p>Total Categories: {len(cached_cats)}</p>
    <hr>
    <h2>Cache Stats:</h2>
    <pre>{stats}</pre>
    """


@admin_bp.route('/benchmark-cache')
@permission_required('manage_settings')
def benchmark_cache():
    """So sánh tốc độ với/không cache"""
    import time
    from app.models.product import Category

    results = {
        'without_cache': [],
        'with_cache': []
    }

    # Test 1: Không cache (query DB trực tiếp)
    cache_manager.clear()  # Xóa cache
    for i in range(10):
        start = time.time()
        cats = Category.query.filter_by(is_active=True).all()
        elapsed = (time.time() - start) * 1000
        results['without_cache'].append(f"{elapsed:.2f}ms")

    # Test 2: Có cache
    cache_manager.set('test_cats', Category.query.filter_by(is_active=True).all())
    for i in range(10):
        start = time.time()
        cats = cache_manager.get('test_cats')
        elapsed = (time.time() - start) * 1000
        results['with_cache'].append(f"{elapsed:.2f}ms")

    avg_no_cache = sum([float(x.replace('ms', '')) for x in results['without_cache']]) / 10
    avg_cache = sum([float(x.replace('ms', '')) for x in results['with_cache']]) / 10

    return f"""
    <h1>Cache Benchmark Results</h1>
    <h2>Không có Cache (Query DB):</h2>
    <p>{results['without_cache']}</p>
    <p><strong>Trung bình: {avg_no_cache:.2f}ms</strong></p>

    <h2>Có Cache (RAM):</h2>
    <p>{results['with_cache']}</p>
    <p><strong>Trung bình: {avg_cache:.2f}ms</strong></p>

    <h2>Kết luận:</h2>
    <p style="color: green; font-size: 20px;">
        Cache nhanh hơn <strong>{(avg_no_cache / avg_cache):.1f}x</strong>
    </p>
    """