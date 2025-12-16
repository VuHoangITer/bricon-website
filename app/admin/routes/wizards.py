# File: app/admin/routes/wizards.py
"""
🧙 Product Selector Wizard Management Routes (Admin)
"""

from flask import render_template, request, flash, redirect, url_for, jsonify
from app import db, cache_manager
from app.models.wizard import Wizard, WizardStep, WizardOption, WizardResult
from app.forms.wizard import WizardForm, WizardStepForm, WizardOptionForm
from app.decorators import permission_required
from app.admin import admin_bp
import json


# ==================== WIZARDS LIST ====================
@admin_bp.route('/wizards')
@permission_required('manage_products')  # Dùng chung permission với products
def wizards():
    """Danh sách wizards"""
    wizards_list = Wizard.query.order_by(Wizard.created_at.desc()).all()
    return render_template('admin/wizard/wizards.html', wizards=wizards_list)


# ==================== ADD WIZARD ====================
@admin_bp.route('/wizards/add', methods=['GET', 'POST'])
@permission_required('manage_products')
def add_wizard():
    """Thêm wizard mới"""
    form = WizardForm()

    if form.validate_on_submit():
        # Nếu set is_default = True, bỏ default của các wizard khác
        if form.is_default.data:
            Wizard.query.update({'is_default': False})

        wizard = Wizard(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            icon=form.icon.data or 'bi-magic',
            is_active=form.is_active.data,
            is_default=form.is_default.data
        )

        try:
            db.session.add(wizard)
            db.session.commit()
            flash(f'✅ Đã tạo wizard "{wizard.name}"!', 'success')
            return redirect(url_for('admin.wizard_steps', wizard_id=wizard.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/wizard_form.html',
                           form=form, title='Tạo Wizard mới')


# ==================== EDIT WIZARD ====================
@admin_bp.route('/wizards/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_products')
def edit_wizard(id):
    """Sửa wizard"""
    wizard = Wizard.query.get_or_404(id)
    form = WizardForm(obj=wizard)

    if form.validate_on_submit():
        # Nếu set is_default = True, bỏ default của các wizard khác
        if form.is_default.data and not wizard.is_default:
            Wizard.query.filter(Wizard.id != id).update({'is_default': False})

        wizard.name = form.name.data
        wizard.slug = form.slug.data
        wizard.description = form.description.data
        wizard.icon = form.icon.data or 'bi-magic'
        wizard.is_active = form.is_active.data
        wizard.is_default = form.is_default.data

        try:
            db.session.commit()
            flash(f'✅ Đã cập nhật wizard "{wizard.name}"!', 'success')
            return redirect(url_for('admin.wizards'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/wizard_form.html',
                           form=form, title=f'Sửa: {wizard.name}', wizard=wizard)


# ==================== DELETE WIZARD ====================
@admin_bp.route('/wizards/delete/<int:id>')
@permission_required('manage_products')
def delete_wizard(id):
    """Xóa wizard"""
    wizard = Wizard.query.get_or_404(id)
    db.session.delete(wizard)
    db.session.commit()
    flash('✅ Đã xóa wizard!', 'success')
    return redirect(url_for('admin.wizards'))


# ==================== WIZARD STEPS ====================
@admin_bp.route('/wizards/<int:wizard_id>/steps')
@permission_required('manage_products')
def wizard_steps(wizard_id):
    """Quản lý steps của wizard"""
    wizard = Wizard.query.get_or_404(wizard_id)
    steps = WizardStep.query.filter_by(wizard_id=wizard_id) \
        .order_by(WizardStep.step_number).all()
    return render_template('admin/wizard/steps.html', wizard=wizard, steps=steps)


# ==================== ADD STEP ====================
@admin_bp.route('/wizards/<int:wizard_id>/steps/add', methods=['GET', 'POST'])
@permission_required('manage_products')
def add_step(wizard_id):
    """Thêm step mới"""
    wizard = Wizard.query.get_or_404(wizard_id)
    form = WizardStepForm()

    # Auto-suggest next step number
    if request.method == 'GET':
        last_step = WizardStep.query.filter_by(wizard_id=wizard_id) \
            .order_by(WizardStep.step_number.desc()).first()
        form.step_number.data = (last_step.step_number + 1) if last_step else 1

    if form.validate_on_submit():
        step = WizardStep(
            wizard_id=wizard_id,
            step_number=form.step_number.data,
            question_text=form.question_text.data,
            description=form.description.data,
            step_type=form.step_type.data,
            is_required=form.is_required.data
        )

        try:
            db.session.add(step)
            db.session.commit()
            flash(f'✅ Đã thêm bước {step.step_number}!', 'success')
            return redirect(url_for('admin.step_options', step_id=step.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/step_form.html',
                           form=form, wizard=wizard, title='Thêm bước mới')


# ==================== EDIT STEP ====================
@admin_bp.route('/wizards/steps/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_products')
def edit_step(id):
    """Sửa step"""
    step = WizardStep.query.get_or_404(id)
    wizard = step.wizard
    form = WizardStepForm(obj=step)

    if form.validate_on_submit():
        step.step_number = form.step_number.data
        step.question_text = form.question_text.data
        step.description = form.description.data
        step.step_type = form.step_type.data
        step.is_required = form.is_required.data

        try:
            db.session.commit()
            flash(f'✅ Đã cập nhật bước {step.step_number}!', 'success')
            return redirect(url_for('admin.wizard_steps', wizard_id=wizard.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/step_form.html',
                           form=form, wizard=wizard, step=step,
                           title=f'Sửa bước {step.step_number}')


# ==================== DELETE STEP ====================
@admin_bp.route('/wizards/steps/delete/<int:id>')
@permission_required('manage_products')
def delete_step(id):
    """Xóa step"""
    step = WizardStep.query.get_or_404(id)
    wizard_id = step.wizard_id
    db.session.delete(step)
    db.session.commit()
    flash('✅ Đã xóa bước!', 'success')
    return redirect(url_for('admin.wizard_steps', wizard_id=wizard_id))


# ==================== STEP OPTIONS ====================
@admin_bp.route('/wizards/steps/<int:step_id>/options')
@permission_required('manage_products')
def step_options(step_id):
    """Quản lý options của step"""
    step = WizardStep.query.get_or_404(step_id)
    options = WizardOption.query.filter_by(step_id=step_id) \
        .order_by(WizardOption.order).all()
    return render_template('admin/wizard/options.html',
                           step=step, options=options, wizard=step.wizard)


# ==================== ADD OPTION ====================
@admin_bp.route('/wizards/steps/<int:step_id>/options/add', methods=['GET', 'POST'])
@permission_required('manage_products')
def add_option(step_id):
    """Thêm option mới"""
    step = WizardStep.query.get_or_404(step_id)
    form = WizardOptionForm()

    if form.validate_on_submit():
        # Parse tags JSON
        tags = None
        if form.tags.data:
            try:
                tags = json.loads(form.tags.data)
            except:
                flash('⚠️ Tags không đúng định dạng JSON, bỏ qua', 'warning')

        option = WizardOption(
            step_id=step_id,
            option_text=form.option_text.data,
            description=form.description.data,
            icon_class=form.icon_class.data,
            emoji=form.emoji.data,
            tags=tags,
            order=form.order.data or 0
        )

        try:
            db.session.add(option)
            db.session.commit()
            flash(f'✅ Đã thêm lựa chọn "{option.option_text}"!', 'success')
            return redirect(url_for('admin.step_options', step_id=step_id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/option_form.html',
                           form=form, step=step, wizard=step.wizard,
                           title='Thêm lựa chọn mới')


# ==================== EDIT OPTION ====================
@admin_bp.route('/wizards/options/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_products')
def edit_option(id):
    """Sửa option"""
    option = WizardOption.query.get_or_404(id)
    step = option.step
    form = WizardOptionForm(obj=option)

    # Load tags vào form
    if request.method == 'GET' and option.tags:
        form.tags.data = json.dumps(option.tags, ensure_ascii=False, indent=2)

    if form.validate_on_submit():
        # Parse tags JSON
        tags = None
        if form.tags.data:
            try:
                tags = json.loads(form.tags.data)
            except:
                flash('⚠️ Tags không đúng định dạng JSON, giữ nguyên giá trị cũ', 'warning')
                tags = option.tags

        option.option_text = form.option_text.data
        option.description = form.description.data
        option.icon_class = form.icon_class.data
        option.emoji = form.emoji.data
        option.tags = tags
        option.order = form.order.data or 0

        try:
            db.session.commit()
            flash(f'✅ Đã cập nhật lựa chọn "{option.option_text}"!', 'success')
            return redirect(url_for('admin.step_options', step_id=step.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'danger')

    return render_template('admin/wizard/option_form.html',
                           form=form, step=step, option=option,
                           wizard=step.wizard, title=f'Sửa: {option.option_text}')


# ==================== DELETE OPTION ====================
@admin_bp.route('/wizards/options/delete/<int:id>')
@permission_required('manage_products')
def delete_option(id):
    """Xóa option"""
    option = WizardOption.query.get_or_404(id)
    step_id = option.step_id
    db.session.delete(option)
    db.session.commit()
    flash('✅ Đã xóa lựa chọn!', 'success')
    return redirect(url_for('admin.step_options', step_id=step_id))


# ==================== WIZARD RESULTS/ANALYTICS ====================
@admin_bp.route('/wizards/<int:wizard_id>/results')
@permission_required('manage_products')
def wizard_results(wizard_id):
    """Xem kết quả/analytics của wizard"""
    wizard = Wizard.query.get_or_404(wizard_id)
    page = request.args.get('page', 1, type=int)

    results = WizardResult.query.filter_by(wizard_id=wizard_id) \
        .order_by(WizardResult.created_at.desc()) \
        .paginate(page=page, per_page=20, error_out=False)

    # Thống kê
    total_uses = wizard.total_results

    return render_template('admin/wizard/results.html',
                           wizard=wizard, results=results, total_uses=total_uses)