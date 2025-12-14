"""
Status: 200 (OK), 302 (Redirect to login), 401/403 (Unauthorized)

Chạy: python test/test_admin_routes.py
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

# Danh sách routes admin cần test
ADMIN_ROUTES = [
    # Auth
    ("/admin/login", "🔐 Login", "GET"),

    # Dashboard
    ("/admin/dashboard", "📊 Dashboard", "GET"),
    ("/admin/welcome", "👋 Welcome", "GET"),

    # Banners
    ("/admin/banners", "🎨 Danh sách Banner", "GET"),
    ("/admin/banners/add", "➕ Thêm Banner", "GET"),

    # Blogs
    ("/admin/blogs", "📝 Danh sách Blog", "GET"),
    ("/admin/blogs/add", "➕ Thêm Blog", "GET"),

    # Categories
    ("/admin/categories", "📁 Danh mục", "GET"),
    ("/admin/categories/add", "➕ Thêm Danh mục", "GET"),

    # Products
    ("/admin/products", "🛍️ Sản phẩm", "GET"),
    ("/admin/products/add", "➕ Thêm Sản phẩm", "GET"),

    # Projects
    ("/admin/projects", "🏗️ Dự án", "GET"),
    ("/admin/projects/add", "➕ Thêm Dự án", "GET"),

    # Jobs
    ("/admin/jobs", "💼 Tuyển dụng", "GET"),
    ("/admin/jobs/add", "➕ Thêm Tuyển dụng", "GET"),

    # FAQs
    ("/admin/faqs", "❓ FAQ", "GET"),
    ("/admin/faqs/add", "➕ Thêm FAQ", "GET"),

    # Contacts
    ("/admin/contacts", "📧 Liên hệ", "GET"),

    # Media
    ("/admin/media", "🖼️ Thư viện Media", "GET"),
    ("/admin/media/upload", "⬆️ Upload Media", "GET"),

    # Users
    ("/admin/users", "👥 Người dùng", "GET"),
    ("/admin/users/add", "➕ Thêm User", "GET"),

    # Roles & Permissions
    ("/admin/roles", "🔑 Vai trò", "GET"),
    ("/admin/roles/add", "➕ Thêm Vai trò", "GET"),
    ("/admin/permissions", "🔐 Quyền hạn", "GET"),

    # Settings
    ("/admin/settings", "⚙️ Cài đặt", "GET"),

    # Quiz
    ("/admin/quizzes", "📝 Quản lý Quiz", "GET"),
    ("/admin/quizzes/add", "➕ Thêm Quiz", "GET"),
    ("/admin/results", "📊 Kết quả Quiz", "GET"),
]


def check_server():
    """Kiểm tra server có chạy không"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return True
    except RequestException:
        return False


def test_route(route, name, method):
    """
    Test một route admin
    Chấp nhận: 200 (OK), 302 (Redirect to login), 401/403 (Unauthorized)
    """
    url = BASE_URL + route

    try:
        if method == "GET":
            response = requests.get(url, timeout=10, allow_redirects=False)
        else:
            response = requests.post(url, timeout=10, allow_redirects=False)

        status = response.status_code

        # Status codes được chấp nhận
        if status == 200:
            print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.CYAN}{url}{Colors.END}")
            return True
        elif status == 302:
            # Redirect (thường là chưa login)
            location = response.headers.get('Location', '')
            if '/admin/login' in location or 'login' in location.lower():
                print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.YELLOW}(→ Login required){Colors.END}")
                return True
            else:
                print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.YELLOW}(→ Redirect){Colors.END}")
                return True
        elif status in [401, 403]:
            # Unauthorized/Forbidden (cũng OK - route tồn tại nhưng không có quyền)
            print(f"{Colors.GREEN}✅{Colors.END} {name:<40} {Colors.YELLOW}(🔒 No permission){Colors.END}")
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


def main():
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}🧪 TEST ADMIN ROUTES {Colors.END}")
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
    print(f"{Colors.BLUE}📍 TEST ADMIN ROUTES{Colors.END}")
    print("=" * 80 + "\n")

    passed = 0
    failed = 0

    for route, name, method in ADMIN_ROUTES:
        if test_route(route, name, method):
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}📊 KẾT QUẢ TEST{Colors.END}")
    print("=" * 80 + "\n")

    total = len(ADMIN_ROUTES)
    print(f"  {Colors.GREEN}✅ Passed: {passed}/{total}{Colors.END}")
    print(f"  {Colors.RED}❌ Failed: {failed}/{total}{Colors.END}")

    if failed > 0:
        percentage = (passed / total) * 100
        print(f"  {Colors.YELLOW}📈 Success rate: {percentage:.1f}%{Colors.END}")

    print(f"\n{'=' * 80}")
    if failed == 0:
        print(f"{Colors.GREEN}🎉 TẤT CẢ ADMIN ROUTES ĐỀU HOẠT ĐỘNG TỐT!{Colors.END}")
    else:
        print(f"{Colors.RED}⚠️  CÓ {failed} ROUTES BỊ LỖI - KIỂM TRA LẠI!{Colors.END}")
    print(f"{'=' * 80}\n")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Test bị hủy bởi user{Colors.END}\n")
        sys.exit(1)