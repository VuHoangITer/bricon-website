"""
❓ FAQs Management Routes
Quản lý câu hỏi thường gặp

FEATURES:
- CRUD cơ bản
- Order để sắp xếp thứ tự hiển thị
- Active/Inactive status
- WYSIWYG Editor cho answer (HTML support)

FIELDS:
- question: Câu hỏi * (255 chars)
- answer: Câu trả lời * (Text/HTML)
- order: Thứ tự hiển thị (số thực)
- is_active: Hiển thị/ẩn

🔒 Permission: manage_faqs

DISPLAY FRONTEND:
- Accordion/Collapse UI
- Sắp xếp theo order (ASC)
- Chỉ hiển thị is_active=True
"""

from flask import render_template, request, flash, redirect, url_for
from app import db
from app.models.content import FAQ
from app.forms.content import FAQForm
from app.decorators import permission_required
from app.admin import admin_bp
from app.models.features import feature_required

# ==================== LIST ====================
@admin_bp.route('/faqs')
@permission_required('manage_faqs')
@feature_required('faqs')
def faqs():
    """
    📋 Danh sách FAQ
    - Sắp xếp theo order (tăng dần)
    - Drag & drop để reorder (future feature)
    """
    faqs = FAQ.query.order_by(FAQ.order).all()
    return render_template('admin/faq/faqs.html', faqs=faqs)


# ==================== ADD ====================
@admin_bp.route('/faqs/add', methods=['GET', 'POST'])
@permission_required('manage_faqs')
@feature_required('faqs')
def add_faq():
    """
    ➕ Thêm FAQ mới

    TIPS:
    - Question: Ngắn gọn, rõ ràng
    - Answer: Chi tiết, có thể dùng HTML
    - Order: Để 0 nếu muốn xuất hiện đầu tiên
    """
    form = FAQForm()

    if form.validate_on_submit():
        faq = FAQ(
            question=form.question.data,
            answer=form.answer.data,
            order=form.order.data or 0,
            is_active=form.is_active.data
        )

        db.session.add(faq)
        db.session.commit()

        flash('Đã thêm FAQ thành công!', 'success')
        return redirect(url_for('admin.faqs'))

    return render_template('admin/faq/faq_form.html', form=form, title='Thêm FAQ')


# ==================== EDIT ====================
@admin_bp.route('/faqs/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_faqs')
@feature_required('faqs')
def edit_faq(id):
    """
    ✏️ Sửa FAQ

    - Load dữ liệu hiện tại
    - Giữ nguyên order nếu không thay đổi
    """
    faq = FAQ.query.get_or_404(id)
    form = FAQForm(obj=faq)

    if form.validate_on_submit():
        faq.question = form.question.data
        faq.answer = form.answer.data
        faq.order = form.order.data or 0
        faq.is_active = form.is_active.data

        db.session.commit()

        flash('Đã cập nhật FAQ thành công!', 'success')
        return redirect(url_for('admin.faqs'))

    return render_template('admin/faq/faq_form.html', form=form, title='Sửa FAQ')



# ==================== DELETE ====================
@admin_bp.route('/faqs/delete/<int:id>')
@permission_required('manage_faqs')
@feature_required('faqs')
def delete_faq(id):
    """
    🗑️ Xóa FAQ

    - Xóa trực tiếp, không có confirmation
    - Có thể thêm soft delete (is_deleted) nếu cần
    """
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()

    flash('Đã xóa FAQ thành công!', 'success')
    return redirect(url_for('admin.faqs'))