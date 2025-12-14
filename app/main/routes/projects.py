from flask import render_template, request, redirect, url_for
from app.main import main_bp
from app import db
from app.models.media import Project
from app.project_config import PROJECT_TYPES
from sqlalchemy.orm import load_only
from app.models.features import feature_required

@main_bp.route('/du-an')
@feature_required('projects')
def projects():
    """Trang danh sách dự án"""
    page = request.args.get('page', 1, type=int)
    project_type = request.args.get('type', '')

    query = (Project.query
             .options(
        load_only(
            Project.id, Project.slug, Project.title, Project.image,
            Project.description, Project.location, Project.year,
            Project.project_type, Project.is_featured
        )
    )
             .filter_by(is_active=True)
             )

    if project_type:
        query = query.filter_by(project_type=project_type)

    projects = query.order_by(Project.year.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    featured_projects = (Project.query
                         .options(load_only(Project.slug, Project.title, Project.image))
                         .filter_by(is_featured=True, is_active=True)
                         ).limit(6).all()

    return render_template('public/du_an/projects.html',
                           projects=projects,
                           featured_projects=featured_projects,
                           project_types=PROJECT_TYPES,
                           current_type=project_type)


@main_bp.route('/du-an/<slug>')
@feature_required('projects')
def project_detail(slug):
    """Trang chi tiết dự án"""
    project = Project.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Tăng lượt xem
    project.view_count += 1
    db.session.commit()

    # Dự án liên quan
    related = (Project.query
    .options(load_only(Project.slug, Project.title, Project.image, Project.location))
    .filter(
        Project.id != project.id,
        Project.project_type == project.project_type,
        Project.is_active == True
    )
    ).limit(2).all()

    return render_template('public/du_an/project_detail.html',
                           project=project,
                           related=related)