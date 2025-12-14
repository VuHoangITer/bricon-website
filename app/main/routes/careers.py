from flask import render_template, request, redirect, url_for
from app.main import main_bp
from app import db
from app.models.job import Job
from app.models.features import feature_required

@main_bp.route('/tuyen-dung')
@feature_required('careers')
def careers():
    """Trang tuyển dụng"""
    department = request.args.get('dept', '')
    location = request.args.get('loc', '')

    query = Job.query.filter_by(is_active=True)

    if department:
        query = query.filter_by(department=department)
    if location:
        query = query.filter_by(location=location)

    jobs = query.order_by(Job.is_urgent.desc(), Job.created_at.desc()).all()

    # Lấy danh sách phòng ban và địa điểm unique
    departments = db.session.query(Job.department).filter_by(is_active=True).distinct().all()
    locations = db.session.query(Job.location).filter_by(is_active=True).distinct().all()

    return render_template('public/tuyen_dung/careers.html',
                           jobs=jobs,
                           departments=[d[0] for d in departments if d[0]],
                           locations=[l[0] for l in locations if l[0]])


@main_bp.route('/tuyen-dung/<slug>')
@feature_required('careers')
def job_detail(slug):
    """Trang chi tiết tuyển dụng"""
    job = Job.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Tăng lượt xem
    job.view_count += 1
    db.session.commit()

    # Các vị trí khác
    other_jobs = Job.query.filter(
        Job.id != job.id,
        Job.is_active == True
    ).order_by(Job.is_urgent.desc()).limit(5).all()

    return render_template('public/tuyen_dung/job_detail.html',
                           job=job,
                           other_jobs=other_jobs)