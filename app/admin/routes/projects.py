"""
Quản lý dự án tiêu biểu

FIELDS:
- title: Tên dự án *
- slug: URL slug *
- client: Tên khách hàng
- location: Địa điểm
- year: Năm thực hiện
- description: Mô tả ngắn
- content: Nội dung chi tiết (HTML)
- image: Ảnh đại diện *
- gallery: JSON array ảnh (multiple)
- project_type: Loại dự án * (từ PROJECT_TYPE_CHOICES)
- area: Diện tích
- products_used: Sản phẩm đã sử dụng (Text)
- is_featured: Dự án nổi bật
- is_active: Hiển thị/ẩn
- view_count: Số lượt xem

🔒 Permissions:
- view_projects: Xem danh sách
- manage_projects: CRUD dự án


FRONTEND DISPLAY:
- List: Filter by project_type
- Detail: Gallery slider, Products used, Client info
"""

from flask import render_template, request, flash, redirect, url_for
from app import db
from app.models.media import Project
from app.forms.media import ProjectForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.admin.utils.helpers import get_image_from_form
from app.models.features import feature_required

# ==================== LIST ====================
@admin_bp.route('/projects')
@permission_required('view_projects')
@feature_required('projects')
def projects():
    """
    📋 Danh sách dự án
    - Phân trang 20 items/page
    - Sắp xếp theo created_at (mới nhất)
    - Badge "Featured" cho dự án nổi bật
    """
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/du_an/projects.html', projects=projects)



# ==================== ADD ====================
@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@permission_required('manage_projects')
@feature_required('projects')
def add_project():
    """
    ➕ Thêm dự án mới

    REQUIRED FIELDS:
    - title, project_type

    TIPS:
    - Image: Chọn ảnh đẹp nhất làm đại diện
    - Gallery: Sẽ implement upload multiple sau
    - Products used: List các sản phẩm Bricon đã dùng
    """
    form = ProjectForm()

    if form.validate_on_submit():
        image_path = get_image_from_form(form.image, 'image', folder='projects')

        project = Project(
            title=form.title.data,
            slug=form.slug.data,
            client=form.client.data,
            location=form.location.data,
            year=form.year.data,
            description=form.description.data,
            content=form.content.data,
            image=image_path,
            project_type=form.project_type.data,
            area=form.area.data,
            products_used=form.products_used.data,
            is_featured=form.is_featured.data,
            is_active=form.is_active.data
        )

        db.session.add(project)
        db.session.commit()

        flash('Đã thêm dự án thành công!', 'success')
        return redirect(url_for('admin.projects'))

    return render_template('admin/du_an/project_form.html', form=form, title='Thêm dự án')



# ==================== EDIT ====================
@admin_bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_projects')
@feature_required('projects')
def edit_project(id):
    """
    ✏️ Sửa dự án

    - Load dữ liệu hiện tại
    - Upload ảnh mới sẽ thay thế ảnh cũ
    - Gallery management (future feature)
    """
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        new_image = get_image_from_form(form.image, 'image', folder='projects')
        if new_image:
            project.image = new_image

        project.title = form.title.data
        project.slug = form.slug.data
        project.client = form.client.data
        project.location = form.location.data
        project.year = form.year.data
        project.description = form.description.data
        project.content = form.content.data
        project.project_type = form.project_type.data
        project.area = form.area.data
        project.products_used = form.products_used.data
        project.is_featured = form.is_featured.data
        project.is_active = form.is_active.data

        db.session.commit()

        flash('Đã cập nhật dự án thành công!', 'success')
        return redirect(url_for('admin.projects'))

    return render_template('admin/du_an/project_form.html', form=form, title='Sửa dự án', project=project)



# ==================== DELETE ====================
@admin_bp.route('/projects/delete/<int:id>')
@permission_required('manage_projects')
@feature_required('projects')
def delete_project(id):
    """
    🗑️ Xóa dự án

    - Xóa khi project không còn hợp lệ
    - Hoặc set is_active=False để archive
    """
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()

    flash('Đã xóa dự án thành công!', 'success')
    return redirect(url_for('admin.projects'))
