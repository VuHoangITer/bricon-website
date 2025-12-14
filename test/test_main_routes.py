"""
Chạy: python test/test_main_routes.py
"""

import sys
import requests
from requests.exceptions import RequestException


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


BASE_URL = "http://localhost:5000"

# Danh sách routes public cần test
PUBLIC_ROUTES = [
    # Home & Static
    ("/", "🏠 Trang chủ"),
    ("/gioi-thieu", "ℹ️ Giới thiệu"),
    ("/chinh-sach", "📜 Chính sách"),

    # Products
    ("/san-pham", "🛍️ Danh sách sản phẩm"),
    ("/san-pham?search=test", "🔍 Tìm kiếm sản phẩm"),
    ("/san-pham?sort=price_asc", "📊 Sắp xếp sản phẩm theo giá"),
    ("/san-pham?sort=latest", "🆕 Sản phẩm mới nhất"),

    # Blog
    ("/tin-tuc", "📰 Danh sách blog"),
    ("/tin-tuc?search=test", "🔍 Tìm kiếm blog"),
    ("/tin-tuc?page=1", "📄 Phân trang blog"),

    # Contact
    ("/lien-he", "📧 Liên hệ"),

    # Projects
    ("/du-an", "🏗️ Danh sách dự án"),
    ("/du-an?page=1", "📄 Phân trang dự án"),

    # Careers
    ("/tuyen-dung", "💼 Tuyển dụng"),
    ("/tuyen-dung?page=1", "📄 Phân trang tuyển dụng"),

    # FAQ
    ("/cau-hoi-thuong-gap", "❓ FAQ"),

    # Search
    ("/tim-kiem?q=test", "🔍 Tìm kiếm tổng hợp"),
    ("/tim-kiem?q=", "🔍 Tìm kiếm rỗng (redirect)"),

    # SEO & Misc
    ("/sitemap.xml", "🗺️ Sitemap"),
    ("/robots.txt", "🤖 Robots.txt"),
]


def check_server():
    """Kiểm tra server có chạy không"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return True
    except RequestException:
        return False


def test_route(route, name):
    """Test một route public"""
    url = BASE_URL + route

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        status = response.status_code

        if status == 200:
            # Check content type cho các file đặc biệt
            content_type = response.headers.get('Content-Type', '')

            if route.endswith('.xml'):
                if 'xml' in content_type:
                    print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.CYAN}{url}{Colors.END}")
                    return True
                else:
                    print(f"{Colors.YELLOW}⚠️{Colors.END} {name:<40} {Colors.YELLOW}Wrong content-type{Colors.END}")
                    return False
            elif route.endswith('.txt'):
                if 'text' in content_type:
                    print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.CYAN}{url}{Colors.END}")
                    return True
                else:
                    print(f"{Colors.YELLOW}⚠️{Colors.END} {name:<40} {Colors.YELLOW}Wrong content-type{Colors.END}")
                    return False
            else:
                print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.CYAN}{url}{Colors.END}")
                return True

        elif status == 302 or status == 301:
            # Redirect (có thể là redirect từ URL cũ sang mới)
            print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.YELLOW}(→ Redirect){Colors.END}")
            return True
        elif status == 404:
            print(f"{Colors.RED}❌{Colors.END} {name:<40} {Colors.RED}404 Not Found{Colors.END}")
            return False
        elif status == 500:
            print(f"{Colors.RED}❌{Colors.END} {name:<40} {Colors.RED}500 Server Error{Colors.END}")
            return False
        else:
            print(f"{Colors.YELLOW}⚠️{Colors.END} {name:<40} {Colors.YELLOW}Status: {status}{Colors.END}")
            return False

    except RequestException as e:
        print(f"{Colors.RED}❌{Colors.END} {name:<40} {Colors.RED}Connection error{Colors.END}")
        return False


def test_template_rendering():
    """Test xem có template nào bị lỗi không"""
    print(f"\n{Colors.BLUE}🎨 KIỂM TRA TEMPLATE RENDERING{Colors.END}\n")

    # Các trang quan trọng cần check nội dung
    important_pages = [
        ("/", "Trang chủ phải có 'index' hoặc 'trang chủ'"),
        ("/san-pham", "Trang sản phẩm phải có 'sản phẩm'"),
        ("/tin-tuc", "Trang blog phải có 'tin tức' hoặc 'blog'"),
    ]

    passed = 0
    failed = 0

    for route, check_text in important_pages:
        url = BASE_URL + route
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                # Check xem có render HTML không (không phải JSON hoặc lỗi)
                if '<html' in content or '<!doctype' in content:
                    print(f"{Colors.GREEN}✅{Colors.END} Template OK: {route}")
                    passed += 1
                else:
                    print(f"{Colors.RED}❌{Colors.END} Template lỗi: {route} (Không phải HTML)")
                    failed += 1
            else:
                print(f"{Colors.YELLOW}⚠️{Colors.END} Cannot check: {route}")

        except Exception as e:
            print(f"{Colors.RED}❌{Colors.END} Error checking: {route}")
            failed += 1

    return passed, failed


def main():
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}🧪 TEST PUBLIC ROUTES {Colors.END}")
    print("=" * 80 + "\n")

    print(f"🌐 Server URL: {Colors.CYAN}{BASE_URL}{Colors.END}\n")

    # Check server
    print("🔍 Kiểm tra server...")
    if not check_server():
        print(f"{Colors.RED}❌ Server không chạy tại {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Vui lòng chạy: flask run hoặc python run.py{Colors.END}\n")
        sys.exit(1)

    print(f"{Colors.GREEN}✅ Server đang chạy{Colors.END}\n")

    # Test routes
    print("=" * 80)
    print(f"{Colors.BLUE}📍 TEST PUBLIC ROUTES{Colors.END}")
    print("=" * 80 + "\n")

    passed = 0
    failed = 0

    for route, name in PUBLIC_ROUTES:
        if test_route(route, name):
            passed += 1
        else:
            failed += 1

    # Test template rendering
    template_passed, template_failed = test_template_rendering()

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}📊 KẾT QUẢ TEST{Colors.END}")
    print("=" * 80 + "\n")

    total = len(PUBLIC_ROUTES)
    print(f"  {Colors.GREEN}✅ Routes Passed: {passed}/{total}{Colors.END}")
    print(f"  {Colors.RED}❌ Routes Failed: {failed}/{total}{Colors.END}")

    if template_passed > 0 or template_failed > 0:
        print(f"  {Colors.GREEN}✅ Templates OK: {template_passed}{Colors.END}")
        print(f"  {Colors.RED}❌ Templates Error: {template_failed}{Colors.END}")

    if failed > 0:
        percentage = (passed / total) * 100
        print(f"  {Colors.YELLOW}📈 Success rate: {percentage:.1f}%{Colors.END}")

    print(f"\n{'=' * 80}")
    if failed == 0 and template_failed == 0:
        print(f"{Colors.GREEN}🎉 TẤT CẢ PUBLIC ROUTES ĐỀU HOẠT ĐỘNG TỐT!{Colors.END}")
    else:
        total_failed = failed + template_failed
        print(f"{Colors.RED}⚠️  CÓ {total_failed} LỖI - KIỂM TRA LẠI!{Colors.END}")
    print(f"{'=' * 80}\n")

    return 0 if (failed == 0 and template_failed == 0) else 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Test bị hủy bởi user{Colors.END}\n")
        sys.exit(1)