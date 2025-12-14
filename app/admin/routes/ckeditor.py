"""
📝 CKEditor Integration Routes
- Image upload for CKEditor 5
"""
from flask import request, jsonify
from flask_login import login_required
from app.utils import save_upload_file
from app.decorators import permission_required
from app.admin import admin_bp


# ==================== CKEDITOR IMAGE UPLOAD API ====================

@admin_bp.route('/api/ckeditor-upload', methods=['POST'])
@login_required
@permission_required('create_blog')  # ✅ Chỉ người có quyền tạo blog mới upload được
def ckeditor_upload_image():
    """
    API upload ảnh cho CKEditor 5
    CKEditor gửi file với key 'upload'
    Trả về JSON format: {"url": "..."}
    """
    try:
        # ✅ Kiểm tra file có được gửi lên không
        if 'upload' not in request.files:
            return jsonify({'error': {'message': 'Không có file được gửi lên'}}), 400

        file = request.files['upload']

        # ✅ Kiểm tra file có tên không
        if file.filename == '':
            return jsonify({'error': {'message': 'File không hợp lệ'}}), 400

        # ✅ Kiểm tra định dạng file
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if '.' not in file.filename:
            return jsonify({'error': {'message': 'File không có phần mở rộng'}}), 400

        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({'error': {'message': f'Chỉ chấp nhận: {", ".join(allowed_extensions)}'}}), 400

        # ✅ Upload file (sử dụng hàm save_upload_file có sẵn)
        result = save_upload_file(file, folder='blog_content', optimize=True)

        if result:
            # ✅ Xử lý kết quả trả về (có thể là tuple hoặc string)
            if isinstance(result, tuple):
                filepath = result[0]  # (filepath, file_info)
            else:
                filepath = result

            # ✅ Đảm bảo URL đầy đủ để CKEditor hiển thị được
            if filepath.startswith('http://') or filepath.startswith('https://'):
                # URL từ Cloudinary
                image_url = filepath
            else:
                # URL local - cần thêm /static nếu chưa có
                if not filepath.startswith('/static/'):
                    if filepath.startswith('/uploads/'):
                        filepath = '/static' + filepath
                    elif not filepath.startswith('/'):
                        filepath = '/static/uploads/' + filepath
                    else:
                        filepath = '/static' + filepath

                # Tạo URL đầy đủ
                image_url = request.url_root.rstrip('/') + filepath

            # ✅ Trả về đúng format CKEditor yêu cầu
            return jsonify({
                'url': image_url
            })
        else:
            return jsonify({'error': {'message': 'Lỗi khi upload file'}}), 500

    except Exception as e:
        # ✅ Log lỗi để debug
        import traceback
        traceback.print_exc()

        return jsonify({
            'error': {'message': f'Lỗi server: {str(e)}'}
        }), 500