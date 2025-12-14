#!/usr/bin/env python3
"""
CSS Build System - Tách và gộp CSS tự động cho Flask Project
Author: Vũ Văn Hoàng
Usage: python build_css.py [command]
pip install watchdog
"""

import os
import re
from pathlib import Path
from datetime import datetime

# ==================== CẤU HÌNH DỰ ÁN ====================
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / 'app' / 'static'
CSS_DIR = STATIC_DIR / 'css'
MODULES_DIR = CSS_DIR / 'modules'
INPUT_FILE = CSS_DIR / 'style.css'
OUTPUT_FILE = CSS_DIR / 'main.min.css'

# ==================== CẤU TRÚC MODULE CSS ====================
CSS_MODULES = {
    '01-variables.css': {
        'start': '/* ==================== CSS VARIABLES ==================== */',
        'end': '/* ==================== GLOBAL RESET ==================== */',
        'description': 'CSS Variables'
    },
    '02-reset.css': {
        'start': '/* ==================== GLOBAL RESET ==================== */',
        'end': '/* ==================== SCROLLBAR (Unified) ==================== */',
        'description': 'CSS Reset & Global Styles'
    },
    '03-scrollbar.css': {
        'start': '/* ==================== SCROLLBAR (Unified) ==================== */',
        'end': '/* ==================== SKIP LINK (Accessibility) ==================== */',
        'description': 'Unified Scrollbar Styles'
    },
    '04-skip-link.css': {
        'start': '/* ==================== SKIP LINK (Accessibility) ==================== */',
        'end': '/* ==================== UTILITY CLASSES ==================== */',
        'description': 'Skip Link for Accessibility'
    },
    '05-utilities.css': {
        'start': '/* ==================== UTILITY CLASSES ==================== */',
        'end': '/* ==================== ANIMATIONS ==================== */',
        'description': 'Utility Classes'
    },
    '06-animations.css': {
        'start': '/* ==================== ANIMATIONS ==================== */',
        'end': '/* ==================== LOADING STATE ==================== */',
        'description': 'CSS Animations'
    },
    '07-loading.css': {
        'start': '/* ==================== LOADING STATE ==================== */',
        'end': '/* ==================== NAVBAR ==================== */',
        'description': 'Loading States'
    },
    '08-navbar.css': {
        'start': '/* ==================== NAVBAR ==================== */',
        'end': '/* ==================== TOP BAR ==================== */',
        'description': 'Navigation Bar Styles'
    },
    '09-topbar.css': {
        'start': '/* ==================== TOP BAR ==================== */',
        'end': '/* ==================== BANNER CAROUSEL ==================== */',
        'description': 'Top Bar Styles'
    },
    '10-banner.css': {
        'start': '/* ==================== BANNER CAROUSEL ==================== */',
        'end': '/* ==================== BUTTONS ==================== */',
        'description': 'Banner Carousel Styles'
    },
    '11-buttons.css': {
        'start': '/* ==================== BUTTONS ==================== */',
        'end': '/* ==================== SECTIONS ==================== */',
        'description': 'Button Styles'
    },
    '12-sections.css': {
        'start': '/* ==================== SECTIONS ==================== */',
        'end': '/* ==================== MOBILE BLOG CAROUSEL  ==================== */',
        'description': 'Section Styles'
    },
    '13-mobile-blog-carousel.css': {
        'start': '/* ==================== MOBILE BLOG CAROUSEL  ==================== */',
        'end': '/* ==================== PAGINATION ==================== */',
        'description': 'Mobile Blog Carousel'
    },
    '14-pagination.css': {
        'start': '/* ==================== PAGINATION ==================== */',
        'end': '/* ==================== PAGE HEADER & BREADCRUMB ==================== */',
        'description': 'Pagination Component'
    },
    '15-page-header.css': {
        'start': '/* ==================== PAGE HEADER & BREADCRUMB ==================== */',
        'end': '/* ==================== FLOATING ACTION BUTTONS ==================== */',
        'description': 'Page Header & Breadcrumb'
    },
    '16-floating-buttons.css': {
        'start': '/* ==================== FLOATING ACTION BUTTONS ==================== */',
        'end': '/* ==================== SCROLL TO TOP BUTTON ==================== */',
        'description': 'Floating Action Buttons'
    },
    '17-scroll-to-top.css': {
        'start': '/* ==================== SCROLL TO TOP BUTTON ==================== */',
        'end': '/* ==================== FOOTER ==================== */',
        'description': 'Scroll to Top Button'
    },
    '18-footer.css': {
        'start': '/* ==================== FOOTER ==================== */',
        'end': '/* ==================== CHATBOT WIDGET ==================== */',
        'description': 'Footer Styles'
    },
    '19-chatbot.css': {
        'start': '/* ==================== CHATBOT WIDGET ==================== */',
        'end': '/* ==================== ALERTS ==================== */',
        'description': 'Chatbot Widget'
    },
    '20-alerts.css': {
        'start': '/* ==================== ALERTS ==================== */',
        'end': '/* ==================== FEATURED PROJECTS CAROUSEL ==================== */',
        'description': 'Alert Messages'
    },
    '21-featured-projects.css': {
        'start': '/* ==================== FEATURED PROJECTS CAROUSEL ==================== */',
        'end': '/* ==================== WORK PROCESS SECTION ==================== */',
        'description': 'Featured Projects Carousel'
    },
    '22-work-process.css': {
        'start': '/* ==================== WORK PROCESS SECTION ==================== */',
        'end': '/* ==================== ABOUT COMPANY SECTION ==================== */',
        'description': 'Work Process Section'
    },
    '23-about-company.css': {
        'start': '/* ==================== ABOUT COMPANY SECTION ==================== */',
        'end': '/* ==================== WHY CHOOSE US SECTION ==================== */',
        'description': 'About Company Section'
    },
    '24-why-choose-us.css': {
        'start': '/* ==================== WHY CHOOSE US SECTION ==================== */',
        'end': '/* ==================== PROJECT FILTER BUTTONS ==================== */',
        'description': 'Why Choose Us Section'
    },
    '25-project-filters.css': {
        'start': '/* ==================== PROJECT FILTER BUTTONS ==================== */',
        'end': '/* ==================== RETURN & REFUND POLICY STYLES ==================== */',
        'description': 'Project Filter Buttons'
    },
    '26-policy-page.css': {
        'start': '/* ==================== RETURN & REFUND POLICY STYLES ==================== */',
        'end': '/* ==================== FILTER SIDEBAR ==================== */',
        'description': 'Return & Refund Policy Styles'
    },
    '27-filter-sidebar.css': {
        'start': '/* ==================== FILTER SIDEBAR ==================== */',
        'end': '/* ==================== PAGE LOADER ==================== */',
        'description': 'Filter Sidebar'
    },
    '28-page-loader.css': {
        'start': '/* ==================== PAGE LOADER ==================== */',
        'end': '/* ==================== ACCESSIBILITY ==================== */',
        'description': 'Page Loader'
    },
    '29-accessibility.css': {
        'start': '/* ==================== ACCESSIBILITY ==================== */',
        'end': '/* ==================== PRINT STYLES ==================== */',
        'description': 'Accessibility Features'
    },
    '30-print-styles.css': {
        'start': '/* ==================== PRINT STYLES ==================== */',
        'end': '/* ==================== UTILITIES - FINAL ==================== */',
        'description': 'Print Styles'
    },
    '31-utilities-final.css': {
        'start': '/* ==================== UTILITIES - FINAL ==================== */',
        'end': '/* ==================== END OF OPTIMIZED CSS ==================== */',
        'description': 'Final Utilities'
    },
    '32-section-label.css': {
        'start': '/* ==================== END OF OPTIMIZED CSS ==================== */',
        'end': '/* ==================== PRODUCT CARD (Mobile-First) ==================== */',
        'description': 'Section Label & Timeline Fixes'
    },
    '33-product-card.css': {
        'start': '/* ==================== PRODUCT CARD (Mobile-First) ==================== */',
        'end': '/* ==================== BLOG CARD (Mobile-First) ==================== */',
        'description': 'Product Card Component'
    },
    '34-blog-card.css': {
        'start': '/* ==================== BLOG CARD (Mobile-First) ==================== */',
        'end': '/* ==================== CTA SECTION ==================== */',
        'description': 'Blog Card Component'
    },
    '35-nut-cta.css': {
        'start': '/* ==================== CTA SECTION ==================== */',
        'end': '/* ==================== SEARCH PAGE STYLES ==================== */',
        'description': 'CTA SECTION'
    },
    '36-search-html.css': {
        'start': '/* ==================== SEARCH PAGE STYLES ==================== */',
        'end': '/* ==================== LOẠI BỎ OUTLINE KHI FOCUS (Product & Blog) ==================== */',
        'description': 'Search.html'
    },
    '37-fix-duong-vien-card.css': {
        'start': '/* ==================== LOẠI BỎ OUTLINE KHI FOCUS (Product & Blog) ==================== */',
        'end': '/* ==================== NEWSLETTER SECTION ==================== */',
        'description': 'fix đường viền của card blog & product'
    },
    '38-newsletter-section.css': {
        'start': '/* ==================== NEWSLETTER SECTION ==================== */',
        'end': '/* ==================== TESTIMONIALS SECTION ==================== */',
        'description': 'Đăng kí nhận khuyến mãi'
    },
    '39-customer-review-section.css': {
        'start': '/* ==================== TESTIMONIALS SECTION ==================== */',
        'end': '/* ==================== TRUST BADGES ==================== */',
        'description': 'Đánh giá khách hàng'
    },
    '40-trust-badges.css': {
        'start': '/* ==================== TRUST BADGES ==================== */',
        'end': '/* ==================== BLOG TABLE OF CONTENTS ==================== */',
        'description': '4 cái ô vuông tin tưởng'
    },
    '41-tutaomucluc.css': {
        'start': '/* ==================== BLOG TABLE OF CONTENTS ==================== */',
        'end': '/* ==================== CONTACT PAGE CUSTOM STYLES - NAMESPACE: trang-lien-he-vn ==================== */',
        'description': 'tutaomucluc'
    },
    '42-custom-trang-lhe.css': {
        'start': '/* ==================== CONTACT PAGE CUSTOM STYLES - NAMESPACE: trang-lien-he-vn ==================== */',
        'end': '/* ==================== PRODUCTS PAGE - MINIMAL STYLES - NAMESPACE: trang-san-pham-vn ==================== */',
        'description': 'trang liên hệ của công ty'
    },
    '43-custom-trang-sp.css': {
        'start': '/* ==================== PRODUCTS PAGE - MINIMAL STYLES - NAMESPACE: trang-san-pham-vn ==================== */',
        'end': '/* ==================== NAMESPACE: TRANG SẢN PHẨM CHI TIẾT VN ==================== */',
        'description': 'trang sản phẩm'
    },
    '44-custom-trang-sp-chitiet.css': {
        'start': '/* ==================== NAMESPACE: TRANG SẢN PHẨM CHI TIẾT VN ==================== */',
        'end': None,
        'description': 'trang sản phẩm chi tiết'
    }
}


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


def extract_css_section(content, start_marker, end_marker):
    """Trích xuất section CSS giữa 2 marker"""
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


def minify_css(css_content):
    """Minify CSS - loại bỏ comments và khoảng trắng thừa"""
    # Giữ lại comment đầu tiên (header info)
    first_comment = re.search(r'/\*.*?\*/', css_content, flags=re.DOTALL)
    header = first_comment.group(0) if first_comment else ""

    # Loại bỏ tất cả comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

    # Loại bỏ khoảng trắng thừa
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
    css_content = re.sub(r';\s*}', '}', css_content)

    # Loại bỏ dòng trống
    css_content = re.sub(r'\n\s*\n', '\n', css_content)

    return (header + "\n" + css_content.strip()) if header else css_content.strip()


def split_css(input_file):
    """Tách file CSS lớn thành các module nhỏ"""
    print_header("🎨 TÁCH FILE CSS THÀNH CÁC MODULE")

    if not input_file.exists():
        print_error(f"Không tìm thấy file: {input_file}")
        return False

    print_info(f"Đọc file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tạo thư mục modules
    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Tạo thư mục: {MODULES_DIR}")

    print(f"\n📦 Đang tách thành {len(CSS_MODULES)} module...\n")

    total_lines = 0
    total_size = 0
    success_count = 0
    warning_count = 0

    for filename, config in CSS_MODULES.items():
        section = extract_css_section(content, config['start'], config['end'])

        if section:
            output_path = MODULES_DIR / filename

            # Thêm header cho mỗi module
            header = f"""/* ==================== {config['description'].upper()} ====================
 * File: {filename}
 * Auto-generated from style.css
 * Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * ========================================================================== */

"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header + section)

            lines = len(section.split('\n'))
            size = len(section) / 1024
            total_lines += lines
            total_size += size
            success_count += 1

            print(f"  ✓ {filename:35s} | {lines:5d} dòng | {size:7.1f} KB | {config['description']}")
        else:
            warning_count += 1
            print_warning(f"{filename:35s} | Không tìm thấy nội dung")

    print(f"\n{'─' * 70}")
    print(f"  📊 Thống kê:")
    print(f"     • Thành công: {success_count}/{len(CSS_MODULES)} files")
    print(f"     • Cảnh báo:   {warning_count} files")
    print(f"     • Tổng dòng:  {total_lines:,} dòng")
    print(f"     • Tổng kích thước: {total_size:,.1f} KB")
    print(f"{'─' * 70}")

    print_success(f"Hoàn tất! Module được lưu tại: {MODULES_DIR}")
    return True


def build_css():
    """Gộp tất cả module thành main.min.css"""
    print_header("🔨 BUILD MAIN.MIN.CSS")

    if not MODULES_DIR.exists():
        print_error(f"Thư mục {MODULES_DIR} không tồn tại!")
        print_info("Chạy: python build_css.py split")
        return False

    combined_css = []
    total_size = 0
    module_count = 0
    missing_files = []

    print("📦 Đang gộp các module...\n")

    # Đọc các module theo thứ tự
    for filename in sorted(CSS_MODULES.keys()):
        file_path = MODULES_DIR / filename

        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_css.append(content)
                size = len(content) / 1024
                total_size += size
                module_count += 1
            print(f"  ✓ {filename:35s} | {size:7.1f} KB")
        else:
            missing_files.append(filename)
            print_warning(f"Không tìm thấy: {filename}")

    # Tạo header cho file build
    build_header = f"""/*! 
 * ============================================================================
 * Main CSS Build 
 * ============================================================================
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * Modules: {module_count} files
 * Total Size: {total_size:.1f} KB (before minification)
 * Description: Auto-generated minified CSS
 * DO NOT EDIT THIS FILE DIRECTLY - Edit individual modules instead
 * ============================================================================
 */

"""

    # Gộp và minify
    full_css = '\n\n'.join(combined_css)
    minified_css = minify_css(full_css)
    final_css = build_header + minified_css

    # Ghi file output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_css)

    # Thống kê
    original_kb = total_size
    minified_kb = len(final_css) / 1024
    saved_kb = original_kb - minified_kb
    saved_percent = (saved_kb / original_kb) * 100 if original_kb > 0 else 0

    print(f"\n{'─' * 70}")
    print(f"  📊 Thống kê Build:")
    print(f"     • Modules thành công:  {module_count}/{len(CSS_MODULES)}")
    if missing_files:
        print(f"     • Modules bị thiếu:    {len(missing_files)}")
    print(f"     • Kích thước gốc:      {original_kb:8.1f} KB")
    print(f"     • Kích thước minify:   {minified_kb:8.1f} KB")
    print(f"     • Tiết kiệm:           {saved_kb:8.1f} KB ({saved_percent:.1f}%)")
    print(f"{'─' * 70}")

    if missing_files:
        print_warning(f"Một số module bị thiếu: {', '.join(missing_files)}")

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

    class CSSChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.css') and 'main.min.css' not in event.src_path:
                print(f"\n🔄 Phát hiện thay đổi: {Path(event.src_path).name}")
                build_css()

    print_header("👀 WATCH MODE - Tự động build khi có thay đổi")
    print_info(f"Đang theo dõi: {MODULES_DIR}")
    print_info("Nhấn Ctrl+C để dừng...\n")

    event_handler = CSSChangeHandler()
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


def show_help():
    """Hiển thị hướng dẫn sử dụng"""
    print_header("📖 HƯỚNG DẪN SỬ DỤNG CSS BUILD SYSTEM")

    print("🔧 Các lệnh có sẵn:\n")

    commands = [
        ("python build_css.py", "Tách + Build (mặc định)", "Lần đầu sử dụng"),
        ("python build_css.py split", "Chỉ tách file CSS", "Tách style.css thành modules"),
        ("python build_css.py build", "Chỉ build CSS", "Gộp modules thành main.min.css"),
        ("python build_css.py watch", "Watch mode", "Tự động build khi sửa file"),
        ("python build_css.py help", "Hiển thị trợ giúp", "Xem hướng dẫn này"),
    ]

    for cmd, desc, note in commands:
        print(f"  {cmd:30s}")
        print(f"    └─ {desc}")
        print(f"       💡 {note}\n")

    print("📁 Cấu trúc thư mục:\n")
    print("  app/")
    print("  └── static/")
    print("      └── css/")
    print("          ├── modules/              ← Các module CSS")
    print("          │   ├── 01-variables.css")
    print("          │   ├── 02-reset.css")
    print("          │   └── ...")
    print("          ├── style.css             ← File CSS gốc")
    print("          └── main.min.css          ← File build (production)\n")

    print("⚡ Workflow khuyến nghị:\n")
    print("  1. Lần đầu:    python build_css.py")
    print("  2. Phát triển: python build_css.py watch")
    print("  3. Production: Deploy main.min.css\n")

    print("🔗 Update template:\n")
    print('  <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/main.min.css\') }}">\n')


def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'split':
            split_css(INPUT_FILE)

        elif command == 'build':
            build_css()

        elif command == 'watch':
            watch_and_build()

        elif command in ['help', '-h', '--help']:
            show_help()

        else:
            print_error(f"Lệnh không hợp lệ: {command}")
            print_info("Chạy 'python build_css.py help' để xem hướng dẫn")

    else:
        # Mặc định: split + build
        print_header("🚀 CSS BUILD SYSTEM - BRICON")
        print_info("Chế độ: Tự động (Split + Build)\n")

        if split_css(INPUT_FILE):
            build_css()

            print("\n" + "=" * 70)
            print("  🎉 HOÀN TẤT!")
            print("=" * 70)
            print("\n💡 Lần sau chỉ cần chạy:")
            print("   • python build_css.py build  (Build lại)")
            print("   • python build_css.py watch  (Auto build)\n")


if __name__ == '__main__':
    main()