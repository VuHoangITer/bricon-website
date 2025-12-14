"""
🛠️ Admin Helper Functions
Các hàm tiện ích dùng chung trong admin
"""

from flask import request
from werkzeug.datastructures import FileStorage
from app.utils import save_upload_file


def get_image_from_form(form_image_field, field_name='image', folder='uploads'):
    """
    🖼️ Lấy đường dẫn ảnh từ form

    Ưu tiên:
    1. Selected image từ Media Picker (request.form.get('selected_image_path'))
    2. File upload từ form field
    3. URL string từ form data

    Args:
        form_image_field: WTForms FileField object
        field_name: Tên field (để debug)
        folder: Thư mục lưu file

    Returns:
        str: Đường dẫn ảnh (URL hoặc /static/...)
        None: Nếu không có ảnh
    """

    from werkzeug.datastructures import FileStorage

    selected_image = request.form.get('selected_image_path')
    if selected_image and selected_image.strip():
        path = selected_image.strip()
        if path.startswith('http://') or path.startswith('https://'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        if not path.startswith('/static/'):
            if path.startswith('/uploads/'):
                path = '/static' + path
            else:
                path = '/static/' + path.lstrip('/')
        return path

    if form_image_field and form_image_field.data:
        if isinstance(form_image_field.data, FileStorage):
            result = save_upload_file(form_image_field.data, folder=folder, optimize=True)
            if result and isinstance(result, tuple):
                filepath = result[0]
                return filepath
            return result
        elif isinstance(form_image_field.data, str):
            return form_image_field.data

    return None


def normalize_filepath(filepath):
    """
    🔧 Chuẩn hóa filepath để đảm bảo có thể hiển thị được

    Examples:
        'uploads/image.jpg' -> '/static/uploads/image.jpg'
        'https://cloudinary.com/...' -> 'https://cloudinary.com/...'
    """

    if not filepath:
        return ''

    # URL đầy đủ - giữ nguyên
    if filepath.startswith('http://') or filepath.startswith('https://'):
        return filepath

    # Thêm / ở đầu
    if not filepath.startswith('/'):
        filepath = '/' + filepath

    # Thêm /static/
    if not filepath.startswith('/static/'):
        if filepath.startswith('/uploads/'):
            filepath = '/static' + filepath
        else:
            filepath = '/static/' + filepath.lstrip('/')

    return filepath