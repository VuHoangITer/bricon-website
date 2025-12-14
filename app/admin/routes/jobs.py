"""
💼 Jobs/Careers Management Routes
Quản lý tin tuyển dụng

FEATURES:
- CRUD đầy đủ
- Deadline tracking (tự động expire)
- Job type, level, salary fields
- WYSIWYG Editor cho description, requirements, benefits
- Urgent flag
- View count tracking

FIELDS:
- title: Vị trí tuyển dụng *
- slug: URL slug *
- department: Phòng ban
- location: Địa điểm làm việc *
- job_type: Full-time/Part-time/Contract/Internship
- level: Intern/Fresher/Junior/Middle/Senior/Lead/Manager
- salary: Mức lương *
- experience: Kinh nghiệm yêu cầu
- description: Mô tả công việc * (HTML)
- requirements: Yêu cầu ứng viên (HTML list)
- benefits: Quyền lợi (HTML list)
- deadline: Hạn nộp hồ sơ (DateField)
- contact_email: Email nhận CV *
- is_active: Đang tuyển
- is_urgent: Tuyển gấp (badge)
- view_count: Số lượt xem

🔒 Permissions:
- view_jobs: Xem danh sách
- manage_jobs: CRUD tin tuyển dụng

AUTO FEATURES:
- is_expired() method: Kiểm tra deadline
- Badge "Expired" cho tin hết hạn
- Badge "Urgent" cho tuyển gấp
- created_at_vn, deadline_vn: VN timezone

FRONTEND DISPLAY:
- List: Filter by department, job_type, location
- Detail: Apply button → Email CV
"""

from flask import render_template, request, flash, redirect, url_for
from app import db
from app.models.job import Job
from app.forms.job import JobForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.models.features import feature_required

# ==================== LIST ====================
@admin_bp.route('/jobs')
@permission_required('view_jobs')
@feature_required('careers')
def jobs():
    """
    📋 Danh sách tuyển dụng
    - Phân trang 20 items/page
    - Sắp xếp theo created_at (mới nhất)
    - Badge: Urgent, Expired, Active
    """
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/tuyen_dung/jobs.html', jobs=jobs)



# ==================== ADD ====================
@admin_bp.route('/jobs/add', methods=['GET', 'POST'])
@permission_required('manage_jobs')
@feature_required('careers')
def add_job():
    """
    ➕ Thêm tin tuyển dụng mới

    REQUIRED FIELDS:
    - title, location, salary, contact_email

    TIPS:
    - Requirements/Benefits: Dùng <ul><li> cho dễ đọc
    - Deadline: Thường 2-4 tuần từ ngày đăng
    """
    form = JobForm()

    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            slug=form.slug.data,
            department=form.department.data,
            location=form.location.data,
            job_type=form.job_type.data,
            level=form.level.data,
            salary=form.salary.data,
            experience=form.experience.data,
            description=form.description.data,
            requirements=form.requirements.data,
            benefits=form.benefits.data,
            deadline=form.deadline.data,
            contact_email=form.contact_email.data,
            is_active=form.is_active.data,
            is_urgent=form.is_urgent.data
        )

        db.session.add(job)
        db.session.commit()

        flash('Đã thêm tin tuyển dụng thành công!', 'success')
        return redirect(url_for('admin.jobs'))

    return render_template('admin/tuyen_dung/job_form.html', form=form, title='Thêm tin tuyển dụng')



# ==================== EDIT ====================
@admin_bp.route('/jobs/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_jobs')
@feature_required('careers')
def edit_job(id):
    """
    ✏️ Sửa tin tuyển dụng

    - Load dữ liệu hiện tại
    - Có thể gia hạn deadline
    - Toggle is_active để đóng/mở tuyển dụng
    """
    job = Job.query.get_or_404(id)
    form = JobForm(obj=job)

    if form.validate_on_submit():
        job.title = form.title.data
        job.slug = form.slug.data
        job.department = form.department.data
        job.location = form.location.data
        job.job_type = form.job_type.data
        job.level = form.level.data
        job.salary = form.salary.data
        job.experience = form.experience.data
        job.description = form.description.data
        job.requirements = form.requirements.data
        job.benefits = form.benefits.data
        job.deadline = form.deadline.data
        job.contact_email = form.contact_email.data
        job.is_active = form.is_active.data
        job.is_urgent = form.is_urgent.data

        db.session.commit()

        flash('Đã cập nhật tin tuyển dụng thành công!', 'success')
        return redirect(url_for('admin.jobs'))

    return render_template('admin/tuyen_dung/job_form.html', form=form, title='Sửa tin tuyển dụng', job=job)



# ==================== DELETE ====================
@admin_bp.route('/jobs/delete/<int:id>')
@permission_required('manage_jobs')
@feature_required('careers')
def delete_job(id):
    """
    🗑️ Xóa tin tuyển dụng

    - Xóa sau khi đã tuyển đủ người
    - Hoặc set is_active=False để archive
    """
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()

    flash('Đã xóa tin tuyển dụng thành công!', 'success')
    return redirect(url_for('admin.jobs'))
