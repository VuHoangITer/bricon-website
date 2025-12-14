"""
🖼️ Media Library Management Routes
- List media với SEO score filter
- Upload media (single/multiple)
- Edit SEO metadata
- Bulk edit
- Album management
- API cho Media Picker

🔒 Permissions:
- view_media: Xem thư viện
- upload_media: Upload files
- edit_media: Chỉnh sửa metadata
- delete_media: Xóa files
- manage_albums: Quản lý albums
"""

import os
import shutil
import logging
from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.media import Media
from app.models.settings import get_setting
from app.forms import MediaSEOForm
from app.utils import save_upload_file, delete_file, get_albums
from app.decorators import permission_required
from app.admin import admin_bp
from app.models.features import feature_required

# ==================== QUẢN LÝ MEDIA LIBRARY ====================
@admin_bp.route('/media')
@permission_required('view_media')
@feature_required('media')
def media():
    """Trang quản lý Media Library với SEO status"""
    page = request.args.get('page', 1, type=int)
    album_filter = request.args.get('album', '')
    seo_filter = request.args.get('seo', '')

    query = Media.query
    if album_filter:
        query = query.filter_by(album=album_filter)

    media_files = query.order_by(Media.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    # File: routes.py - bên trong hàm media()
    query = Media.query
    if album_filter:
        query = query.filter_by(album=album_filter)

    media_files = query.order_by(Media.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    albums = get_albums()
    total_files = Media.query.count()
    total_size = db.session.query(db.func.sum(Media.file_size)).scalar() or 0
    total_size_mb = round(total_size / (1024 * 1024), 2)


    return render_template(
        'admin/media/media.html',
        media_files=media_files,
        albums=albums,
        total_files=total_files,
        total_size_mb=total_size_mb,
        current_album=album_filter
    )


@admin_bp.route('/media/upload', methods=['GET', 'POST'])
@permission_required('upload_media')
@feature_required('media')
def upload_media():
    """Upload media files với SEO optimization"""
    if request.method == 'POST':
        files = request.files.getlist('files')
        album = request.form.get('album', '').strip()
        folder = request.form.get('folder', 'general')
        default_alt_text = request.form.get('default_alt_text', '').strip()
        auto_alt_text = request.form.get('auto_alt_text') == 'on'

        if not files or not files[0].filename:
            flash('Vui lòng chọn file để upload!', 'warning')
            return redirect(url_for('admin.upload_media'))

        uploaded_count = 0
        errors = []

        for file in files:
            if file and file.filename:
                try:
                    # ✅ Tạo alt_text cho từng file
                    if default_alt_text:
                        file_alt_text = default_alt_text
                    elif auto_alt_text:
                        from app.utils import slugify
                        name_without_ext = os.path.splitext(file.filename)[0]
                        file_alt_text = name_without_ext.replace('-', ' ').replace('_', ' ').title()
                    else:
                        file_alt_text = None

                    # ✅ Upload file
                    filepath, file_info = save_upload_file(
                        file,
                        folder=folder,
                        album=album if album else None,
                        alt_text=file_alt_text,
                        optimize=True
                    )

                    if filepath and file_info:
                        # ✅ Tạo Media object từ file_info
                        media = Media(
                            filename=file_info.get('filename'),
                            original_filename=file_info.get('original_filename'),
                            filepath=file_info.get('filepath'),  # Cloudinary URL hoặc /static/...
                            file_type=file_info.get('file_type'),
                            file_size=file_info.get('file_size'),
                            width=file_info.get('width', 0),
                            height=file_info.get('height', 0),
                            album=file_info.get('album'),
                            alt_text=file_alt_text,
                            title=file_alt_text,
                            uploaded_by=current_user.id
                        )

                        db.session.add(media)
                        uploaded_count += 1
                    else:
                        errors.append(f"Không thể upload {file.filename}")

                except Exception as e:
                    errors.append(f"Lỗi upload {file.filename}: {str(e)}")
                    import traceback
                    traceback.print_exc()  # ✅ Print full error để debug

        if uploaded_count > 0:
            try:
                db.session.commit()
                flash(f'✅ Đã upload thành công {uploaded_count} file!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Lỗi lưu database: {str(e)}', 'danger')

        if errors:
            for error in errors:
                flash(error, 'danger')

        return redirect(url_for('admin.media'))

    # GET request - hiển thị form
    albums = get_albums()
    return render_template('admin/media/media_upload.html', albums=albums)


@admin_bp.route('/media/create-album', methods=['POST'])
@permission_required('manage_albums')
@feature_required('media')
def create_album():
    """Tạo album mới"""
    album_name = request.form.get('album_name', '').strip()

    if not album_name:
        flash('Vui lòng nhập tên album!', 'warning')
        return redirect(url_for('admin.media'))

    album_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'albums',
        secure_filename(album_name)
    )

    try:
        os.makedirs(album_path, exist_ok=True)
        flash(f'Đã tạo album "{album_name}" thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi tạo album: {str(e)}', 'danger')

    return redirect(url_for('admin.media'))


@admin_bp.route('/media/delete/<int:id>')
@permission_required('delete_media')
@feature_required('media')
def delete_media(id):
    """Xóa media file (Cloudinary + local + DB)"""
    from app.utils import delete_file
    import logging

    logging.basicConfig(level=logging.INFO)
    def safe_print(*args):
        try:
            print(*args)
        except Exception:
            pass

    media = Media.query.get_or_404(id)
    album_name = media.album

    try:
        if media.filepath and "res.cloudinary.com" in media.filepath:
            safe_print(f"[Delete Cloudinary Start]: {repr(media.filepath)}")
            res = delete_file(media.filepath)
            safe_print(f"[Delete Cloudinary Result]: {res}")
        else:
            safe_print("[Delete Cloudinary]: Bỏ qua (không phải URL Cloudinary)")

        if media.filepath and media.filepath.startswith('/static/'):
            file_path = media.filepath.replace('/static/', '')
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], '..', file_path)
            abs_path = os.path.abspath(full_path)

            if os.path.exists(abs_path):
                os.remove(abs_path)
                safe_print(f"[Delete Local]: Đã xóa {abs_path}")
            else:
                safe_print(f"[Delete Local]: Không tìm thấy {abs_path}")

    except Exception as e:
        safe_print(f"[Delete Error]: {e}")
        logging.exception(e)

    try:
        db.session.delete(media)
        db.session.commit()
        flash('🗑️ Đã xóa ảnh khỏi hệ thống', 'success')
        safe_print("[DB Delete]: Media record removed successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa khỏi cơ sở dữ liệu: {e}', 'danger')
        safe_print(f"[DB Delete Error]: {e}")
        logging.exception(e)

    if album_name:
        return redirect(url_for('admin.media', album=album_name))
    return redirect(url_for('admin.media'))


@admin_bp.route('/media/delete-album/<album_name>')
@permission_required('manage_albums')
@feature_required('media')
def delete_album(album_name):
    """Xóa album (chỉ khi rỗng)"""
    remaining_files = Media.query.filter_by(album=album_name).count()

    if remaining_files > 0:
        flash(f'Không thể xóa album có {remaining_files} file! Vui lòng xóa hết file trước.', 'danger')
        return redirect(url_for('admin.media'))

    album_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'albums',
        secure_filename(album_name)
    )

    try:
        if os.path.exists(album_path):
            shutil.rmtree(album_path)
        flash(f'Đã xóa album "{album_name}" thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa album "{album_name}": {str(e)}', 'danger')

    return redirect(url_for('admin.media'))


@admin_bp.route('/media/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('edit_media')
@feature_required('media')
def edit_media(id):
    """Sửa thông tin media với SEO fields và hiển thị điểm SEO"""
    from app.forms.media import MediaSEOForm

    media = Media.query.get_or_404(id)
    form = MediaSEOForm(obj=media)

    if form.validate_on_submit():
        media.alt_text = form.alt_text.data.strip()
        media.title = form.title.data.strip() if form.title.data else None
        media.caption = form.caption.data.strip() if form.caption.data else None
        media.album = form.album.data.strip() if form.album.data else None

        if not media.alt_text:
            flash('Alt Text là bắt buộc cho SEO!', 'warning')
            albums = get_albums()
            return render_template('admin/media/media_edit.html',
                                   media=media,
                                   form=form,
                                   albums=albums)

        if len(media.alt_text) < 10:
            flash('Alt Text quá ngắn! Nên từ 30-125 ký tự.', 'warning')

        if not media.title:
            media.title = media.alt_text

        try:
            db.session.commit()

            flash('✓ Đã cập nhật thông tin media!', 'success')

            if media.album:
                return redirect(url_for('admin.media', album=media.album))
            return redirect(url_for('admin.media'))

        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi lưu: {str(e)}', 'danger')

    albums = get_albums()

    return render_template('admin/media/media_edit.html',
                           media=media,
                           form=form,
                           albums=albums)


@admin_bp.route('/media/bulk-edit', methods=['POST'])
@permission_required('edit_media')
@feature_required('media')
def bulk_edit_media():
    """Bulk edit SEO cho nhiều media"""
    media_ids = request.form.getlist('media_ids[]')
    action = request.form.get('action')

    if not media_ids:
        return jsonify({'success': False, 'message': 'Chưa chọn file nào'})

    if action == 'set_alt_text':
        alt_text_template = request.form.get('alt_text_template', '')
        updated = 0

        for media_id in media_ids:
            media = Media.query.get(media_id)
            if media:
                alt_text = alt_text_template.replace('{filename}', media.original_filename)
                if media.album:
                    alt_text = alt_text.replace('{album}', media.album)

                media.alt_text = alt_text
                updated += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'Đã cập nhật {updated} file'})

    elif action == 'set_album':
        album_name = request.form.get('album_name', '')
        updated = Media.query.filter(Media.id.in_(media_ids)).update(
            {Media.album: album_name},
            synchronize_session=False
        )
        db.session.commit()
        return jsonify({'success': True, 'message': f'Đã chuyển {updated} file vào album "{album_name}"'})

    return jsonify({'success': False, 'message': 'Action không hợp lệ'})



# ==================== API CHO MEDIA PICKER ====================
@admin_bp.route('/api/media')
@permission_required('view_media')
@feature_required('media')
def api_media():
    """API trả về danh sách media với đường dẫn chuẩn hóa"""
    album = request.args.get('album', '')
    search = request.args.get('search', '')

    query = Media.query
    if album:
        query = query.filter_by(album=album)
    if search:
        query = query.filter(Media.original_filename.ilike(f'%{search}%'))

    media_list = query.order_by(Media.created_at.desc()).limit(100).all()

    albums_data = get_albums()
    album_names = [a['name'] if isinstance(a, dict) else a for a in albums_data]

    def normalize_filepath(media):
        """Chuẩn hóa filepath để đảm bảo có thể hiển thị được"""
        filepath = media.filepath

        if not filepath:
            return ''

        if filepath.startswith('http://') or filepath.startswith('https://'):
            return filepath

        if not filepath.startswith('/'):
            filepath = '/' + filepath

        if not filepath.startswith('/static/'):
            if filepath.startswith('/uploads/'):
                filepath = '/static' + filepath
            else:
                filepath = '/static/' + filepath.lstrip('/')

        return filepath

    return jsonify({
        'media': [{
            'id': m.id,
            'filename': m.filename,
            'original_filename': m.original_filename,
            'filepath': normalize_filepath(m),
            'width': m.width or 0,
            'height': m.height or 0,
            'album': m.album or ''
        } for m in media_list],
        'albums': album_names
    })
