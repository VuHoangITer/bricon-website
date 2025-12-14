#!/usr/bin/env python3
"""
JavaScript Build System - Tách và gộp JS tự động cho Flask Project
Author: Vũ Văn Hoàng
Usage: python build_js.py [command]
pip install watchdog
"""

import os
import re
from pathlib import Path
from datetime import datetime

# ==================== CẤU HÌNH DỰ ÁN ====================
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / 'app' / 'static'
JS_DIR = STATIC_DIR / 'js'
MODULES_DIR = JS_DIR / 'modules'
INPUT_FILE = JS_DIR / 'main.js'
OUTPUT_FILE = JS_DIR / 'main.min.js'

# ==================== CẤU TRÚC MODULE JAVASCRIPT ====================
JS_MODULES = {
    '01-floating-buttons.js': {
        'start': '// ==================== FLOATING BUTTONS ====================',
        'end': '// ==================== ANIMATE ON SCROLL ====================',
        'description': 'NÚT HÀNH ĐỘNG NỔI',
        'details': '''
        📍 Vị trí: Góc phải màn hình
        🎯 Chức năng: Hiển thị các nút floating (Phone, Zalo, Messenger)
        📄 Sử dụng tại: 
           - layouts/base.html (component floating-buttons)
           - Tất cả các trang public
        🔧 Hoạt động: Luôn hiển thị khi scroll, style.display = "flex"
        '''
    },
    '02-animate-scroll.js': {
        'start': '// ==================== ANIMATE ON SCROLL ====================',
        'end': '// ==================== AUTO DISMISS ALERTS ====================',
        'description': 'HIỆU ỨNG CUỘN TRANG',
        'details': '''
        📍 Vị trí: Áp dụng cho tất cả card
        🎯 Chức năng: Tự động thêm animation khi card xuất hiện trong viewport
        📄 Sử dụng tại:
           - components/card_product.html (thẻ sản phẩm)
           - components/card_blog.html (thẻ tin tức)
        🔧 Hoạt động: 
           - Dùng IntersectionObserver API
           - Thêm class "animate-on-scroll" khi element vào màn hình
           - threshold: 0.1 (10% element hiển thị)
        '''
    },
    '03-auto-dismiss-alerts.js': {
        'start': '// ==================== AUTO DISMISS ALERTS ====================',
        'end': '// ==================== SEARCH FORM VALIDATION ====================',
        'description': 'TỰ ĐỘNG ĐÓNG THÔNG BÁO',
        'details': '''
        📍 Vị trí: Mọi trang có flash messages
        🎯 Chức năng: Tự động đóng thông báo Bootstrap sau 3 giây
        📄 Sử dụng tại:
           - layouts/base.html ({% with messages = get_flashed_messages() %})
           - Các trang admin sau khi submit form
        🔧 Hoạt động:
           - Target: .alert.alert-dismissible
           - Timeout: 3000ms (3 giây)
           - Dùng bootstrap.Alert().close()
        '''
    },
    '04-search-validation.js': {
        'start': '// ==================== SEARCH FORM VALIDATION ====================',
        'end': '// ==================== IMAGE LAZY LOADING ====================',
        'description': 'KIỂM TRA FORM TÌM KIẾM',
        'details': '''
        📍 Vị trí: Thanh tìm kiếm navbar và trang search
        🎯 Chức năng: Ngăn submit form tìm kiếm khi input rỗng
        📄 Sử dụng tại:
           - layouts/base.html (form search trong navbar)
           - public/search.html (trang tìm kiếm chính)
        🔧 Hoạt động:
           - Target: form[action*="search"]
           - Kiểm tra input[name="q"] hoặc input[name="search"]
           - preventDefault() nếu value.trim() === ""
           - Hiện alert "Vui lòng nhập từ khóa tìm kiếm"
        '''
    },
    '05-lazy-loading.js': {
        'start': '// ==================== IMAGE LAZY LOADING ====================',
        'end': '// ==================== SMOOTH SCROLL - FIXED ====================',
        'description': 'TẢI ẢNH CHẬM (LAZY LOAD)',
        'details': '''
        📍 Vị trí: Tất cả ảnh có attribute loading="lazy"
        🎯 Chức năng: Chỉ tải ảnh khi sắp vào viewport, tiết kiệm băng thông
        📄 Sử dụng tại:
           - components/card_product.html (ảnh sản phẩm)
           - components/card_blog.html (ảnh bài viết)
           - public/products.html, blogs.html
        🔧 Hoạt động:
           - Kiểm tra browser có hỗ trợ native lazy loading
           - Nếu CÓ: Dùng img[data-src] → img.src
           - Nếu KHÔNG: Tải lazysizes.min.js từ CDN làm fallback
        '''
    },
    '06-smooth-scroll.js': {
        'start': '// ==================== SMOOTH SCROLL - FIXED ====================',
        'end': '// ==================== SCROLL TO TOP WITH PROGRESS ====================',
        'description': 'CUỘN MỀM MẠI ANCHOR',
        'details': '''
        📍 Vị trí: Tất cả link có href="#..."
        🎯 Chức năng: Cuộn mượt mà đến section thay vì nhảy đột ngột
        📄 Sử dụng tại:
           - Navbar menu links (href="#about", "#products")
           - Banner CTA buttons (href="#featured-projects")
           - Footer quick links
        🔧 Hoạt động:
           - BỎ QUA nếu có data-bs-toggle (Bootstrap tabs)
           - BỎ QUA nếu href chỉ là "#" đơn thuần
           - Kiểm tra element có tồn tại trước khi scroll
           - Offset: -120px (tránh bị che bởi navbar fixed)
           - behavior: "smooth"
        ⚠️ Lưu ý: Fixed để không conflict với Bootstrap components
        '''
    },
    '07-scroll-to-top.js': {
        'start': '// ==================== SCROLL TO TOP WITH PROGRESS ====================',
        'end': '// ==================== BANNER LAZY LOAD + RESPONSIVE (INTEGRATED) ====================',
        'description': 'NÚT LÊN ĐẦU TRANG + TIẾN TRÌNH',
        'details': '''
        📍 Vị trí: Góc phải dưới màn hình
        🎯 Chức năng: 
           - Hiện nút khi scroll > 300px
           - Vòng tròn progress theo % scroll
           - Click để lên đầu trang
        📄 Sử dụng tại:
           - layouts/base.html (id="scrollToTop")
           - CSS: 20-scroll-to-top.css
        🔧 Hoạt động:
           - Dùng SVG circle với strokeDasharray/strokeDashoffset
           - Tính scrollPercentage = scrollTop / scrollHeight
           - Update offset theo % để vẽ progress circle
           - requestAnimationFrame để smooth
           - Show button: scrollTop > 300px
        '''
    },
    '08-banner-carousel.js': {
        'start': '// ==================== BANNER LAZY LOAD + RESPONSIVE (INTEGRATED) ====================',
        'end': '// ==================== RESPONSIVE IMAGE SOURCE HANDLER ====================',
        'description': 'BANNER CAROUSEL TRANG CHỦ',
        'details': '''
        📍 Vị trí: Trang chủ (index.html)
        🎯 Chức năng: Quản lý carousel banner với đầy đủ tính năng
        📄 Sử dụng tại:
           - public/index.html (id="bannerCarousel")
           - CSS: 04-banner.css
        🔧 Các tính năng:
           1. ✅ LAZY LOAD: IntersectionObserver tải ảnh khi cần
           2. ✅ PRELOAD: Tải trước slide hiện tại và 2 slide kế (prev/next)
           3. ✅ PAUSE ON HOVER: Desktop dừng khi hover
           4. ✅ PAUSE ON TOUCH: Mobile dừng khi chạm, resume sau 3s
           5. ✅ KEYBOARD: Arrow Left/Right điều khiển
           6. ✅ REDUCED MOTION: Tôn trọng prefers-reduced-motion
           7. ✅ SMOOTH CTA: Banner buttons scroll mượt
           8. ✅ FALLBACK: Force load tất cả ảnh sau 3s
           9. ✅ ANALYTICS: Track views nếu có Google Analytics/GTM
           10. ✅ PRECONNECT: Nếu dùng Cloudinary/ImgIX CDN
        '''
    },
    '09-responsive-images.js': {
        'start': '// ==================== RESPONSIVE IMAGE SOURCE HANDLER ====================',
        'end': '// ==================== Page-loader ====================',
        'description': 'XỬ LÝ ẢNH RESPONSIVE',
        'details': '''
        📍 Vị trí: Banner carousel (dùng <picture> tag)
        🎯 Chức năng: Force browser đánh giá lại <source> khi resize
        📄 Sử dụng tại:
           - public/index.html (banner với <picture><source media="...">)
        🔧 Hoạt động:
           - Listen resize event (debounced 250ms)
           - Tìm tất cả <picture> trong carousel
           - Set img.src = img.src để trigger re-evaluation
           - Browser tự chọn <source> phù hợp theo media query
        ⚠️ Cần thiết cho Safari/iOS không auto-update picture sources
        '''
    },
    '10-page-loader.js': {
        'start': '// ==================== Page-loader ====================',
        'end': '// ==================== FEATURED PROJECTS CAROUSEL WITH MOUSE DRAG ====================',
        'description': 'LOADING TOÀN TRANG',
        'details': '''
        📍 Vị trí: Tất cả các trang
        🎯 Chức năng: Hiển thị spinner khi trang đang load, ẩn khi xong
        📄 Sử dụng tại:
           - layouts/base.html (id="page-loader")
           - CSS: 17-loading.css
        🔧 Hoạt động:
           - Trigger: window load event
           - Fade out: opacity = 0 (transition 300ms)
           - Remove: setTimeout 300ms để xóa khỏi DOM
        💡 Cải thiện UX khi trang load chậm (hình ảnh lớn, JS nhiều)
        '''
    },
    '11-projects-carousel.js': {
        'start': '// ==================== FEATURED PROJECTS CAROUSEL WITH MOUSE DRAG ====================',
        'end': '// ==================== Chatbot Widget ====================',
        'description': 'CAROUSEL DỰ ÁN NỔI BẬT',
        'details': '''
        📍 Vị trí: Trang chủ section "Dự án nổi bật"
        🎯 Chức năng: Carousel tùy chỉnh với kéo chuột/chạm
        📄 Sử dụng tại:
           - public/index.html (id="projectsCarousel")
           - components/featured_projects.html
           - CSS: 19-featured-projects.css
        🔧 Các tính năng:
           - ✅ MOUSE DRAG: Kéo chuột để chuyển slide (desktop)
           - ✅ TOUCH DRAG: Vuốt ngón tay (mobile)
           - ✅ RUBBER BAND: Hiệu ứng giới hạn khi kéo quá đầu/cuối
           - ✅ AUTO SLIDE: Tự động chuyển sau 3s
           - ✅ DOTS NAVIGATION: Click vào dot để jump slide
           - ✅ KEYBOARD: Arrow keys điều khiển
           - ✅ PAUSE ON HOVER: Dừng auto khi hover
           - ✅ TAB HIDDEN: Dừng khi tab ẩn (visibilitychange)
           - ✅ RESPONSIVE: Tự động điều chỉnh khi resize
        🎨 Cursor: grab → grabbing khi drag
        ⚠️ Threshold: 50px để chuyển slide
        '''
    },
    '12-chatbot.js': {
        'start': '// ==================== Chatbot Widget ====================',
        'end': '// ==================== ENHANCED EFFECTS FOR INDEX PAGE ==================== /',
        'description': 'CHATBOT HỖ TRỢ KHÁCH HÀNG',
        'details': '''
        📍 Vị trí: Góc phải dưới màn hình (trên scroll-to-top)
        🎯 Chức năng: Chatbot AI hỗ trợ khách hàng 24/7
        📄 Sử dụng tại:
           - layouts/base.html (id="chatbotButton", id="chatbotWidget")
           - components/chatbot.html
           - CSS: 26-chatbot.css
           - Backend: app/chatbot/routes.py
        🔧 Các tính năng:
           - ✅ FULL SCREEN MOBILE: Chiếm toàn màn hình trên mobile
           - ✅ NO AUTO-FOCUS: Không tự động mở bàn phím
           - ✅ BODY SCROLL LOCK: Khóa scroll body khi mở (iOS fix)
           - ✅ TYPING INDICATOR: Hiệu ứng "đang gõ..." khi bot trả lời
           - ✅ AUTO SCROLL: Tự động scroll xuống tin nhắn mới
           - ✅ REQUEST LIMIT: Hiển thị số tin nhắn còn lại (20/session)
           - ✅ RESET CHAT: Nút làm mới hội thoại
           - ✅ ERROR HANDLING: Xử lý lỗi mạng, server
           - ✅ INPUT VALIDATION: Giới hạn 500 ký tự
           - ✅ ESCAPE HTML: Bảo mật XSS
        🌐 API Endpoints:
           - POST /chatbot/send → Gửi tin nhắn
           - POST /chatbot/reset → Reset session
        💡 Dùng Flask session để lưu lịch sử chat
        '''
    },
    '13-enhanced-effects.js': {
        'start': '// ==================== ENHANCED EFFECTS FOR INDEX PAGE ==================== /',
        'end': '/*** ==================== MOBILE BLOG CAROUSEL  ============================*/',
        'description': 'HIỆU ỨNG NÂNG CAO TRANG CHỦ',
        'details': '''
    📍 Vị trí: Chỉ áp dụng trên trang chủ (index.html)
    🎯 Chức năng: Bộ hiệu ứng cao cấp để tăng trải nghiệm người dùng
    📄 Sử dụng tại:
       - public/index.html (tất cả sections)
       - CSS: Không cần file riêng, tự inject style
    🔧 Các hiệu ứng bao gồm:
       1. ✅ ANIMATED COUNTER: Đếm tăng dần cho số liệu thống kê
          - Target: .about-stats h3, .stat-number h3
          - Duration: 4000ms (4 giây)
          - Step: 100 (mỗi bước tăng 100)
          - Trigger: IntersectionObserver (threshold: 0.5)
          - Hiệu ứng: Màu chữ chuyển sang brand-primary khi đếm

       2. ✅ PARALLAX SCROLLING: Ảnh di chuyển chậm hơn nội dung
          - Target: .video-container img
          - Speed: 0.3 (30% tốc độ scroll)
          - Throttle: 10ms để tối ưu performance
          - willChange: transform (GPU acceleration)

       3. ✅ SMOOTH REVEAL: Hiệu ứng fade-in mượt mà
          - Target: .product-card, .blog-card, .process-step, section h2
          - Stagger delay: 100ms giữa các elements
          - Animation: opacity 0→1 + translateY(30px→0)
          - Duration: 600ms ease

       4. ✅ MAGNETIC BUTTONS: Nút bị "hút" theo chuột (desktop)
          - Target: .btn-warning, .btn-dark, .btn-outline-warning
          - Loại trừ: .mobile-blog-carousel-btn
          - Movement: 15% của khoảng cách chuột-tâm nút
          - Smooth: transform 0.2s ease-out

       5. ✅ TYPING ANIMATION: Hiệu ứng đánh máy cho heading
          - Target: .about-content h2, #featured-projects h2
          - Speed: 80ms/ký tự
          - Cursor: 2px solid border với blink animation
          - Auto remove cursor sau khi hoàn thành

    🎨 Namespace: window.EnhancedEffects (tránh xung đột)
    🚀 Auto-init: Tự động khởi tạo khi DOM ready
    🧹 Cleanup: Tự động dọn dẹp khi beforeunload

    ⚠️ Lưu ý:
       - Magnetic Buttons CHỈ hoạt động trên desktop (>= 768px)
       - Parallax có throttle để tránh lag
       - Tất cả dùng IntersectionObserver → hiệu suất cao
       - Không xung đột với hiệu ứng animate-on-scroll đã có
    '''
    },
    '14-mobile-blog-carousel.js': {
        'start': '/*** ==================== MOBILE BLOG CAROUSEL  ============================*/',
        'end': '/* ==================== BANNER EFFECTS WITH DRAG/SWIPE ==================== */',
        'description': 'CAROUSEL BLOG MOBILE/TABLET',
        'details': '''
    📍 Vị trí: Trang chủ section "Tin tức nổi bật" (chỉ mobile/tablet)
    🎯 Chức năng: Carousel tùy chỉnh cho blog cards ở màn hình nhỏ
    📄 Sử dụng tại:
       - public/index.html (section #featured-blogs-section)
       - CSS: 13-mobile-blog-carousel.css
    🔧 Các tính năng:
       - ✅ CHỈ HOẠT ĐỘNG: Trang index + màn hình ≤ 991px
       - ✅ AUTO DETECT: Tự động phát hiện trang index qua:
            • URL pathname (/, /index.html, /index)
            • Blog section ID (#featured-blogs-section)
            • Body class/attribute (page-index, data-page="index")
       - ✅ TOUCH/MOUSE DRAG: Vuốt/kéo để chuyển slide
       - ✅ AUTO SLIDE: Tự động chuyển sau 5 giây
       - ✅ DOTS NAVIGATION: Click vào dot để jump slide
       - ✅ PREV/NEXT BUTTONS: Nút điều hướng 2 bên
       - ✅ KEYBOARD: Arrow keys điều khiển
       - ✅ PAUSE ON HOVER: Dừng auto khi hover (desktop/tablet)
       - ✅ TAB HIDDEN: Dừng khi tab ẩn (visibilitychange)
       - ✅ RESPONSIVE: Tự động init/destroy khi resize
       - ✅ NO CONFLICT: Namespace riêng window.MobileBlogCarousel

    🎨 Cursor: grab → grabbing khi drag
    ⚠️ Threshold: 50px để trigger chuyển slide
    🔄 Transition: 400ms cubic-bezier(0.4, 0, 0.2, 1)
    ⏱️ Auto slide interval: 5000ms (5 giây)

    💡 Cách hoạt động:
       1. Kiểm tra shouldActivate() = width ≤ 991px + isIndexPage()
       2. Tìm blog section (#featured-blogs-section)
       3. Tìm blog grid (.row.g-4)
       4. Clone tất cả blog cards vào carousel structure
       5. Ẩn grid gốc (display: none)
       6. Hiển thị carousel với navigation
       7. Khi resize > 991px: destroy carousel, hiện lại grid

    🚀 API Public:
       - window.MobileBlogCarousel.init()
       - window.MobileBlogCarousel.destroy()
       - window.MobileBlogCarousel.nextSlide()
       - window.MobileBlogCarousel.prevSlide()
       - window.MobileBlogCarousel.goToSlide(index)

    ⚠️ Lưu ý quan trọng:
       - Module này CHỈ hoạt động khi có #featured-blogs-section
       - Không ảnh hưởng đến trang khác (products, blogs, contact...)
       - Tự động cleanup khi chuyển trang hoặc resize về desktop
       - Không xung đột với projects-carousel đã có
    '''
    },
    '15-banner-effect.js': {
        'start': '/* ==================== BANNER EFFECTS WITH DRAG/SWIPE ==================== */',
        'end': '/* ==================== Newsletter ==================== */',
        'description': 'BANNER EFFECTS (ANIMATION + DRAG/SWIPE)',
        'details': '''
    📍 Vị trí: Trang chủ (section #bannerCarousel)
    🎯 Chức năng: Hiệu ứng chuyển cảnh và animation chữ trên banner chính
    
    📄 Sử dụng tại:
       - public/index.html (phần đầu trang: banner chính)
       - CSS: 15-banner-effect.css (chứa các animation như fade, slide, zoom)
       - JS: 15-banner-effect.js (namespace riêng BannerEffect)
    
    🔧 Các tính năng:
       - ✅ Hiệu ứng chữ (caption) tự động khi banner xuất hiện
       - ✅ Animation đa dạng: fade-in, slide-up, slide-left, zoom-in
       - ✅ Tùy chọn delay animation (config.animationDelay)
       - ✅ Hoạt động mượt với Bootstrap Carousel
       - ✅ Hỗ trợ IntersectionObserver (chỉ animate khi vào viewport)
       - ✅ Tích hợp drag/swipe (kéo chuột hoặc vuốt để đổi slide)
       - ✅ Tạm dừng auto-slide khi drag hoặc tab ẩn
       - ✅ Resume lại sau khi thả drag
       - ✅ Không xung đột với main.js (namespace: window.BannerEffect)
    
    🎨 Hiệu ứng caption:
       - Xuất hiện mượt với opacity + transform
       - Có thể đặt riêng animation qua data-animation="banner-slide-up"...
    
    ⚙️ Cấu hình chính (BannerEffect.config):
       - carouselId: 'bannerCarousel'
       - animationDelay: 100ms
       - animationTypes: [fade-in, slide-up, slide-left, zoom-in]
       - observerThreshold: 0.2
       - enableDrag: true
       - dragThreshold: 50px
    
    🚀 API Public:
       - BannerEffect.init() → Khởi tạo
       - BannerEffect.destroy() → Cleanup khi rời trang
       - BannerEffect.refresh() → Làm mới caption hiện tại
       - BannerEffect.setAnimationType(type) → Đặt animation mặc định
       - BannerEffect.toggleDrag(true/false) → Bật/tắt drag
    
    ⚠️ Lưu ý quan trọng:
       - Chỉ áp dụng cho section có id="bannerCarousel"
       - Không dùng chung namespace với main.js
       - Nên load sau Bootstrap JS
       - Có cleanup tự động khi unload trang
    
    💡 Mục tiêu:
          1. Thay đổi animation type:
            BannerEffect.setAnimationType('banner-slide-up');
            BannerEffect.refresh();
          2. Bật/tắt drag:
            BannerEffect.toggleDrag(false); // Tắt
            BannerEffect.toggleDrag(true);  // Bật
          3. Refresh animations:
            BannerEffect.refresh();
          4. Destroy (cleanup):
            BannerEffect.destroy();
          5. Set animation per slide (trong HTML):
            <div class="carousel-caption" data-animation="banner-zoom-in">
    '''
    },
    '16-newsletter.js': {
        'start': '/* ==================== Newsletter ==================== */',
        'end': '/* ==================== Testimonials / Customer Reviews ==================== */',
        'description': 'Đăng kí nhận khuyến mãi',
        'details': '''
            Đăng kí nhận khuyến mãi
    '''
    },
    '17-customer-review.js': {
        'start': '/* ==================== Testimonials / Customer Reviews ==================== */',
        'end': '/* ==================== Trust Badges / Certifications ==================== */',
        'description': 'Khách hàng đánh giá',
        'details': '''
            Khách hàng đánh giá
    '''
    },
    '18-bon-o-tin-tuong.js': {
        'start': '/* ==================== Trust Badges / Certifications ==================== */',
        'end': '/* ==================== BLOG TABLE OF CONTENTS ==================== */',
        'description': '4 ô tạo niềm tin',
        'details': '''
        bốn ô tạo niềm tin , hiệu ứng fade-in
    '''
    },
    '19-tutaomucluc.js': {
        'start': '/* ==================== BLOG TABLE OF CONTENTS ==================== */',
        'end': '/* ==================== NavLink Hold Drop ==================== */',
        'description': 'Lịch sử công ty',
        'details': '''
        Lịch sử công ty
    '''
    },
    '20-hold-drop-nav.js': {
        'start': '/* ==================== NavLink Hold Drop ==================== */',
        'end': '/* ==================== Phóng to ảnh sản phẩm ==================== */',
        'description': 'Hold Drop Nav',
        'details': '''
        Chức năng: Giữ chuột vào nav-link sẽ hiện dropdown
    '''
    },
    '21-phong-to-anh.js': {
        'start': '/* ==================== Phóng to ảnh sản phẩm ==================== */',
        'end': None,
        'description': ' Phóng to ảnh sản phẩm ',
        'details': '''
    Chức năng: bấm vào kính lúp phóng to ảnh
'''
    },
}

# ==================== HÀM TIỆN ÍCH ====================
def print_header(title):
    """In header đẹp"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message):
    """In thông báo thành công"""
    print(f"✅ {message}")


def print_error(message):
    """In thông báo lỗi"""
    print(f"❌ {message}")


def print_info(message):
    """In thông báo thông tin"""
    print(f"ℹ️  {message}")


def print_warning(message):
    """In thông báo cảnh báo"""
    print(f"⚠️  {message}")


# ==================== HÀM XỬ LÝ JAVASCRIPT ====================
def extract_js_section(content, start_marker, end_marker):
    """Trích xuất section JS giữa 2 marker"""
    if not start_marker:
        return ""

    start_idx = content.find(start_marker)
    if start_idx == -1:
        return ""

    if end_marker:
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            return content[start_idx:]
        return content[start_idx:end_idx]

    return content[start_idx:]


def minify_js(js_content):
    """Minify JavaScript - loại bỏ comments và khoảng trắng thừa (cơ bản)"""
    # Giữ lại comment đầu tiên (header info)
    first_comment = re.search(r'/\*.*?\*/', js_content, flags=re.DOTALL)
    header = first_comment.group(0) if first_comment else ""

    # Loại bỏ single-line comments (cẩn thận với URLs)
    js_content = re.sub(r'(?<!:)//.*?$', '', js_content, flags=re.MULTILINE)

    # Loại bỏ multi-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)

    # Loại bỏ khoảng trắng thừa (giữ nguyên strings)
    js_content = re.sub(r'\n\s*\n', '\n', js_content)

    # Loại bỏ trailing spaces
    js_content = re.sub(r'[ \t]+$', '', js_content, flags=re.MULTILINE)

    return (header + "\n" + js_content.strip()) if header else js_content.strip()


def split_js(input_file):
    """Tách file JS lớn thành các module nhỏ"""
    print_header("🎯 TÁCH FILE JAVASCRIPT THÀNH CÁC MODULE")

    if not input_file.exists():
        print_error(f"Không tìm thấy file: {input_file}")
        return False

    print_info(f"Đọc file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tạo thư mục modules
    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Tạo thư mục: {MODULES_DIR}")

    print(f"\n📦 Đang tách thành {len(JS_MODULES)} module...\n")

    total_lines = 0
    total_size = 0

    for filename, config in JS_MODULES.items():
        section = extract_js_section(content, config['start'], config['end'])

        if section:
            output_path = MODULES_DIR / filename

            # Thêm header chi tiết bằng tiếng Việt
            header = f"""/**
 * ==================== {config['description']} ====================
 * File: {filename}
 * Tạo tự động từ: main.js
 * Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
 * ==========================================================================
 * 
{config['details']}
 * ==========================================================================
 */

"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header + section)

            lines = len(section.split('\n'))
            size = len(section) / 1024
            total_lines += lines
            total_size += size

            print(f"  {filename:32s} | {lines:5d} dòng | {size:7.1f} KB | {config['description']}")
        else:
            print_warning(f"{filename:32s} | Không tìm thấy nội dung")

    print(f"\n{'─' * 70}")
    print(f"  Tổng cộng: {len(JS_MODULES)} files | {total_lines:5d} dòng | {total_size:7.1f} KB")
    print(f"{'─' * 70}")

    print_success(f"Hoàn tất! Module được lưu tại: {MODULES_DIR}")
    return True


def build_js():
    """Gộp tất cả module thành main.min.js"""
    print_header("🔨 BUILD MAIN.MIN.JS")

    if not MODULES_DIR.exists():
        print_error(f"Thư mục {MODULES_DIR} không tồn tại!")
        print_info("Chạy: python build_js.py split")
        return False

    combined_js = []
    total_size = 0
    module_count = 0

    print("📦 Đang gộp các module...\n")

    # Đọc các module theo thứ tự
    for filename in sorted(JS_MODULES.keys()):
        file_path = MODULES_DIR / filename

        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_js.append(content)
                size = len(content) / 1024
                total_size += size
                module_count += 1
            print(f"  ✓ {filename:32s} | {size:7.1f} KB")
        else:
            print_warning(f"Không tìm thấy: {filename}")

    # Tạo header cho file build
    build_header = f"""/*! 
 * ============================================================================
 * Main JavaScript Build
 * ============================================================================
 * Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
 * Modules: {module_count} files
 * Description: Auto-generated optimized JavaScript
 * DO NOT EDIT THIS FILE DIRECTLY - Edit individual modules instead
 * ============================================================================
 */

"use strict";

"""

    # Gộp và minify
    full_js = '\n\n'.join(combined_js)
    minified_js = minify_js(full_js)
    final_js = build_header + minified_js

    # Ghi file output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_js)

    # Thống kê
    original_kb = total_size
    minified_kb = len(final_js) / 1024
    saved_kb = original_kb - minified_kb
    saved_percent = (saved_kb / original_kb) * 100 if original_kb > 0 else 0

    print(f"\n{'─' * 70}")
    print(f"  📊 Thống kê Build:")
    print(f"     • Kích thước gốc:    {original_kb:8.1f} KB")
    print(f"     • Kích thước minify: {minified_kb:8.1f} KB")
    print(f"     • Tiết kiệm:         {saved_kb:8.1f} KB ({saved_percent:.1f}%)")
    print(f"{'─' * 70}")

    print_success(f"Build thành công: {OUTPUT_FILE}")
    return True


def watch_and_build():
    """Watch mode - tự động build khi có thay đổi"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print_error("Cần cài đặt watchdog!")
        print_info("Chạy: pip install watchdog")
        return

    class JSChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.js') and 'main.min.js' not in event.src_path:
                print(f"\n🔄 Phát hiện thay đổi: {Path(event.src_path).name}")
                build_js()

    print_header("👀 WATCH MODE - Tự động build khi có thay đổi")
    print_info(f"Đang theo dõi: {MODULES_DIR}")
    print_info("Nhấn Ctrl+C để dừng...\n")

    event_handler = JSChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(MODULES_DIR), recursive=False)
    observer.start()

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n")
        print_info("Đã dừng watch mode")

    observer.join()


def list_modules():
    """Liệt kê chi tiết tất cả các module"""
    print_header("📋 DANH SÁCH CHI TIẾT CÁC MODULE JAVASCRIPT")

    print(f"Tổng số module: {len(JS_MODULES)}\n")

    for i, (filename, config) in enumerate(JS_MODULES.items(), 1):
        print(f"\n{'=' * 70}")
        print(f"📦 MODULE #{i:02d}: {filename}")
        print(f"{'=' * 70}")
        print(f"📌 Tên: {config['description']}")
        print(config['details'])

    print(f"\n{'=' * 70}")
    print(f"💡 Để xem code chi tiết, mở file trong thư mục: {MODULES_DIR}")
    print(f"{'=' * 70}\n")


def show_help():
    """Hiển thị hướng dẫn sử dụng"""
    print_header("📖 HƯỚNG DẪN SỬ DỤNG JAVASCRIPT BUILD SYSTEM")

    print("🔧 Các lệnh có sẵn:\n")

    commands = [
        ("python build_js.py", "Tách + Build (mặc định)", "Lần đầu sử dụng"),
        ("python build_js.py split", "Chỉ tách file JS", "Tách main.js thành modules"),
        ("python build_js.py build", "Chỉ build JS", "Gộp modules thành main.min.js"),
        ("python build_js.py watch", "Watch mode", "Tự động build khi sửa file"),
        ("python build_js.py list", "Liệt kê modules", "Xem chi tiết từng module"),
        ("python build_js.py help", "Hiển thị trợ giúp", "Xem hướng dẫn này"),
    ]

    for cmd, desc, note in commands:
        print(f"  {cmd:30s}")
        print(f"    └─ {desc}")
        print(f"       💡 {note}\n")

    print("📁 Cấu trúc thư mục:\n")
    print("  app/")
    print("  └── static/")
    print("      └── js/")
    print("          ├── modules/               ← Các module JavaScript")
    print("          │   ├── 01-floating-buttons.js")
    print("          │   ├── 02-animate-scroll.js")
    print("          │   └── ...")
    print("          ├── main.js                ← File JS gốc")
    print("          └── main.min.js            ← File build (dùng trong production)\n")

    print("⚡ Workflow khuyến nghị:\n")
    print("  1. Lần đầu: python build_js.py")
    print("  2. Phát triển: python build_js.py watch")
    print("  3. Production: Chỉ cần deploy main.min.js\n")

    print("🔗 Update template:\n")
    print('  <script src="{{ url_for(\'static\', filename=\'js/main.min.js\') }}" defer></script>\n')


def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'split':
            split_js(INPUT_FILE)

        elif command == 'build':
            build_js()

        elif command == 'watch':
            watch_and_build()

        elif command == 'list':
            list_modules()

        elif command in ['help', '-h', '--help']:
            show_help()

        else:
            print_error(f"Lệnh không hợp lệ: {command}")
            print_info("Chạy 'python build_js.py help' để xem hướng dẫn")

    else:
        # Mặc định: split + build
        print_header("🚀 JAVASCRIPT BUILD SYSTEM")
        print_info("Chế độ: Tự động (Split + Build)\n")

        if split_js(INPUT_FILE):
            build_js()

            print("\n" + "=" * 70)
            print("  🎉 HOÀN TẤT!")
            print("=" * 70)
            print("\n💡 Lần sau chỉ cần chạy:")
            print("   • python build_js.py build  (Build lại)")
            print("   • python build_js.py watch  (Auto build)")
            print("   • python build_js.py list   (Xem chi tiết modules)\n")


if __name__ == '__main__':
    main()