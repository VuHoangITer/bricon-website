import os
import re
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
import cloudinary.uploader
import pytz

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


# ✅ ========== THÊM MỚI: TIMEZONE UTILITY FUNCTIONS ==========
def get_vn_now():
    """
    Lấy thời gian hiện tại theo múi giờ Việt Nam
    Returns: datetime object với timezone VN
    """
    return datetime.now(VN_TZ)


def utc_to_vn(utc_dt):
    """
    Chuyển đổi UTC datetime sang Việt Nam timezone

    Args:
        utc_dt: datetime object (UTC)

    Returns:
        datetime object với timezone VN hoặc None
    """
    if utc_dt is None:
        return None

    # Nếu datetime chưa có timezone info, gán UTC
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)

    # Chuyển sang múi giờ Việt Nam
    return utc_dt.astimezone(VN_TZ)


def vn_to_utc(vn_dt):
    """
    Chuyển đổi Việt Nam datetime sang UTC
    (Dùng khi cần lưu vào database)

    Args:
        vn_dt: datetime object (VN timezone)

    Returns:
        datetime object với timezone UTC hoặc None
    """
    if vn_dt is None:
        return None

    # Nếu datetime chưa có timezone info, gán VN
    if vn_dt.tzinfo is None:
        vn_dt = VN_TZ.localize(vn_dt)

    # Chuyển sang UTC
    return vn_dt.astimezone(pytz.utc)


def format_vn_datetime(dt, format='%d/%m/%Y %H:%M:%S'):
    """
    Format datetime sang múi giờ VN với custom format

    Args:
        dt: datetime object
        format: string format (default: '%d/%m/%Y %H:%M:%S')

    Returns:
        Formatted string hoặc empty string
    """
    vn_dt = utc_to_vn(dt)
    return vn_dt.strftime(format) if vn_dt else ''


def allowed_file(filename):
    """Kiểm tra file có hợp lệ không"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def slugify(text):
    """
    Chuyển text thành dạng slug-friendly
    - Chuyển tiếng Việt có dấu về không dấu
    """
    text = text.lower()
    # Chuyển tiếng Việt không dấu
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'[đ]', 'd', text)
    # Xóa ký tự đặc biệt
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Thay space bằng dash
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')


def generate_seo_filename(original_filename, alt_text=None):
    """
    Tạo tên file SEO-friendly
    - Ưu tiên dùng alt_text nếu có
    - Loại bỏ ký tự đặc biệt
    - Thêm timestamp để tránh trùng
    """
    name, ext = os.path.splitext(original_filename)

    if alt_text:
        # Sử dụng alt_text làm tên file
        base_name = slugify(alt_text)
    else:
        # Sử dụng tên gốc
        base_name = slugify(name)

    # Giới hạn độ dài (max 50 ký tự)
    base_name = base_name[:50]

    # Thêm timestamp ngắn gọn
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    return f"{base_name}-{timestamp}{ext.lower()}"


import cloudinary.uploader

def save_upload_file(file, folder='general', album=None, alt_text=None, optimize=True):
    """
    Upload file lên Cloudinary thay vì lưu cục bộ.
    - folder: thư mục (products, banners, blogs, ...)
    - album: tên album (sẽ được thêm vào folder nếu có)
    - alt_text: dùng để tạo tên file SEO-friendly
    Returns: (image_url, file_info_dict) hoặc (None, None)
    """
    if not file or not hasattr(file, 'filename') or not allowed_file(file.filename):
        return None, None

    # Tạo tên file SEO-friendly
    filename = generate_seo_filename(file.filename, alt_text)

    # Tạo đường dẫn thư mục trên Cloudinary
    cloud_folder = f"enterprise/{folder}"
    if album:
        cloud_folder = f"{cloud_folder}/{secure_filename(album)}"

    try:
        # Upload lên Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=cloud_folder,
            public_id=os.path.splitext(filename)[0],
            overwrite=True,
            resource_type="image",
            use_filename=True,
            unique_filename=False
        )

        image_url = upload_result.get("secure_url")
        width = upload_result.get("width", 0)
        height = upload_result.get("height", 0)
        file_size = upload_result.get("bytes", 0)
        file_type = upload_result.get("format", "unknown")

        file_info = {
            'filename': filename,
            'original_filename': file.filename,
            'filepath': image_url,  # URL Cloudinary
            'file_type': file_type,
            'file_size': file_size,
            'width': width,
            'height': height,
            'album': album
        }

        return image_url, file_info

    except Exception as e:
        print(f"[Cloudinary upload error]: {e}")
        return None, None



def delete_file(filepath):
    """Xóa file khỏi Cloudinary hoặc local"""
    try:
        if not filepath or not isinstance(filepath, str):
            print("[Delete Error]: Filepath rỗng hoặc không hợp lệ")
            return False

        # --- Xử lý Cloudinary ---
        if "res.cloudinary.com" in filepath:
            try:
                # Tách public_id đúng định dạng
                parts = filepath.split("/upload/")[-1]  # lấy phần sau /upload/
                parts = parts.split("/")  # ['v1759825641', 'enterprise', 'general', 'cat-say-so-2-20251007152712.png']

                # Nếu phần đầu có version (v1234...) thì bỏ đi
                if parts[0].startswith("v") and parts[0][1:].isdigit():
                    parts = parts[1:]

                # Ghép lại, bỏ phần mở rộng (.jpg, .png,...)
                path_no_ext = "/".join(parts)
                public_id = os.path.splitext(path_no_ext)[0]

                print(f"[Debug] Cloudinary public_id: {public_id}")

                result = cloudinary.uploader.destroy(public_id)
                print(f"[Cloudinary delete]: {public_id} -> {result}")
                return result.get("result") == "ok"

            except Exception as e:
                print(f"[Cloudinary Delete Error]: {e}")
                return False

        # --- Xử lý file local ---
        elif filepath.startswith('/static/'):
            rel_path = filepath.replace('/static/', '', 1).lstrip("\\/")
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            abs_path = os.path.abspath(os.path.join(static_dir, rel_path))

            if not abs_path.startswith(static_dir):
                print(f"[Security Warning]: Path không hợp lệ -> {abs_path}")
                return False

            if os.path.exists(abs_path):
                os.remove(abs_path)
                print(f"[Local delete]: {abs_path}")
                return True
            else:
                print(f"[Delete Warning]: File không tồn tại -> {abs_path}")
                return False

        else:
            print(f"[Delete Skipped]: Không nhận dạng được kiểu đường dẫn ({filepath})")
            return False

    except Exception as e:
        print(f"[Delete Error]: {e}")
        return False

def get_albums():
    """Lấy danh sách albums với số lượng file"""
    from app.models.media import Media
    from sqlalchemy import func

    # Lấy albums từ DB
    album_counts = db.session.query(
        Media.album,
        func.count(Media.id).label('count')
    ).filter(
        Media.album.isnot(None),
        Media.album != ''
    ).group_by(Media.album).all()

    albums_dict = {album_name: count for album_name, count in album_counts}

    # Convert sang list và sort
    albums = [{'name': name, 'count': count} for name, count in albums_dict.items()]
    albums.sort(key=lambda x: x['name'])

    return albums


def handle_image_upload(form_field, field_name, folder='general', alt_text=None):
    """
    Xử lý upload ảnh: ưu tiên từ media library, không thì upload mới

    Args:
        form_field: File từ form (có thể None)
        field_name: Tên field để lấy path từ hidden input
        folder: Thư mục lưu nếu upload mới
        alt_text: Alt text cho SEO (optional)

    Returns:
        str: Đường dẫn ảnh hoặc None
    """
    from flask import request

    # 1. Kiểm tra có chọn từ media library không
    selected_path = request.form.get(f'{field_name}_selected_path', '').strip()
    if selected_path:
        return selected_path

    # 2. Nếu không, upload file mới
    if form_field and hasattr(form_field, "filename") and form_field.filename:
        result = save_upload_file(form_field, folder=folder, alt_text=alt_text, optimize=True)
        return result[0] if isinstance(result, tuple) else result

    # 3. Không có gì cả
    return None


def validate_seo_alt_text(alt_text):
    """
    Validate Alt Text theo chuẩn SEO

    Returns: (is_valid, message)
    """
    if not alt_text or len(alt_text.strip()) == 0:
        return False, "Alt Text không được để trống"

    alt_len = len(alt_text)

    if alt_len < 10:
        return False, f"Alt Text quá ngắn ({alt_len} ký tự). Nên từ 30-125 ký tự"

    if alt_len > 125:
        return False, f"Alt Text quá dài ({alt_len} ký tự). Nên từ 30-125 ký tự"

    # Check spam keywords
    spam_patterns = [
        r'(ảnh|hình|image|picture|photo)\s*\d+',  # ảnh 1, image123
        r'click\s+here',
        r'buy\s+now',
    ]

    for pattern in spam_patterns:
        if re.search(pattern, alt_text.lower()):
            return False, "Alt Text không nên chứa spam keywords như 'ảnh 123', 'click here'"

    if alt_len >= 30 and alt_len <= 125:
        return True, "Alt Text đạt chuẩn SEO"
    else:
        return True, f"Alt Text hợp lệ nhưng nên 30-125 ký tự (hiện tại: {alt_len})"