"""
Helper functions cho models
"""
from app.models.media import Media


def get_media_by_image_url(image_url):
    """
    Tìm Media record từ image URL (Cloudinary hoặc local)

    Hỗ trợ các format:
    - https://res.cloudinary.com/.../image.jpg (Cloudinary)
    - /static/uploads/products/image.jpg (Local)
    - uploads/products/image.jpg (Local không có /)

    Returns: Media object hoặc None
    """
    if not image_url:
        return None

    # Case 1: URL Cloudinary đầy đủ - tìm theo filepath
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return Media.query.filter_by(filepath=image_url).first()

    # Case 2: Local path - tìm theo filename
    # Lấy tên file: /static/uploads/products/abc.jpg → abc.jpg
    filename = image_url.split('/')[-1]

    # Tìm theo filename (ưu tiên)
    media = Media.query.filter_by(filename=filename).first()

    if media:
        return media

    # Case 3: Nếu không tìm thấy, thử chuẩn hóa path và tìm lại
    normalized_path = image_url
    if not normalized_path.startswith('/'):
        normalized_path = '/' + normalized_path
    if not normalized_path.startswith('/static/'):
        if normalized_path.startswith('/uploads/'):
            normalized_path = '/static' + normalized_path
        else:
            normalized_path = '/static/' + normalized_path.lstrip('/')

    return Media.query.filter_by(filepath=normalized_path).first()