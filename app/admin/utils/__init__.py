"""
🛠️ Admin Utilities Package
Helper functions, SEO calculations, file generators
"""

# ==================== HELPER FUNCTIONS ====================
from .helpers import (
    get_image_from_form,  # Lấy ảnh từ form (Media Picker + Upload)
    normalize_filepath,  # Chuẩn hóa đường dẫn file
)

# ==================== FILE GENERATORS ====================
from .generators import (
    generate_sitemap,  # Tạo sitemap.xml
    generate_robots_txt,  # Tạo robots.txt
)

# ✅ Export tất cả để dễ import
__all__ = [
    # Helpers
    'get_image_from_form',
    'normalize_filepath',

    # Generators
    'generate_sitemap',
    'generate_robots_txt',
]