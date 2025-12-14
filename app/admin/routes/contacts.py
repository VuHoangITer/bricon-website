"""
📧 Contacts Management Routes
Quản lý tin nhắn liên hệ từ khách hàng

FEATURES:
- List với filter read/unread
- View detail (tự động đánh dấu đã đọc)
- Delete message
- Filter Newsletter Subscribers
- Không có Add/Edit (chỉ nhận từ form frontend)

FIELDS:
- name: Họ tên khách hàng *
- email: Email *
- phone: Số điện thoại
- subject: Tiêu đề
- message: Nội dung *
- is_read: Đã đọc/chưa đọc (auto set khi view)
- created_at: Thời gian gửi (VN timezone)

🔒 Permissions:
- view_contacts: Xem danh sách
- manage_contacts: Xóa message

WORKFLOW:
1. Khách gửi form → Contact record created
2. Admin vào /admin/contacts → Thấy danh sách
3. Click "Xem chi tiết" → is_read = True
4. Có thể xóa message sau khi xử lý

📊 DASHBOARD INTEGRATION:
- Hiển thị số message chưa đọc trên dashboard
- Badge "New" cho message mới
"""

from flask import render_template, request, flash, redirect, url_for
from app import db
from app.models.contact import Contact
from app.decorators import permission_required
from app.admin import admin_bp
from app.models.features import feature_required

# ==================== LIST ====================
@admin_bp.route('/contacts')
@permission_required('view_contacts')
@feature_required('contacts')
def contacts():
    """
    📋 Danh sách liên hệ
    - Phân trang 20 items/page
    - Sắp xếp theo created_at (mới nhất trên đầu)
    - Hiển thị badge "Mới" cho unread
    - Filter: All / Contact / Newsletter / Unread / Read
    """
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all')  # all, contact, newsletter
    read_status = request.args.get('status', 'all')  # all, read, unread

    # Base query
    query = Contact.query

    # Filter by type
    if filter_type == 'newsletter':
        query = query.filter_by(subject='Đăng ký nhận tin')
    elif filter_type == 'contact':
        query = query.filter(Contact.subject != 'Đăng ký nhận tin')

    # Filter by read status
    if read_status == 'read':
        query = query.filter_by(is_read=True)
    elif read_status == 'unread':
        query = query.filter_by(is_read=False)

    contacts = query.order_by(Contact.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # Statistics
    stats = {
        'total': Contact.query.count(),
        'unread': Contact.query.filter_by(is_read=False).count(),
        'newsletter': Contact.query.filter_by(subject='Đăng ký nhận tin').count(),
        'contacts': Contact.query.filter(Contact.subject != 'Đăng ký nhận tin').count()
    }

    return render_template(
        'admin/lien_he/contacts.html',
        contacts=contacts,
        filter_type=filter_type,
        read_status=read_status,
        stats=stats
    )


# ==================== VIEW DETAIL ====================
@admin_bp.route('/contacts/view/<int:id>')
@permission_required('view_contacts')
@feature_required('contacts')
def view_contact(id):
    """
    👁️ Xem chi tiết liên hệ

    AUTO PROCESSING:
    - Tự động set is_read = True khi view lần đầu
    - Hiển thị đầy đủ thông tin khách hàng
    - Button: Reply (mailto:), Delete

    DISPLAY:
    - Thời gian: VN timezone (created_at_vn)
    - Format: dd/mm/yyyy lúc HH:MM
    """
    contact = Contact.query.get_or_404(id)

    if not contact.is_read:
        contact.is_read = True
        db.session.commit()

    return render_template('admin/lien_he/contact_detail.html', contact=contact)


# ==================== DELETE ====================
@admin_bp.route('/contacts/delete/<int:id>')
@permission_required('manage_contacts')
@feature_required('contacts')
def delete_contact(id):
    """
    🗑️ Xóa liên hệ

    - Xóa sau khi đã xử lý xong
    - Không thể khôi phục
    """
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()

    flash('Đã xóa liên hệ thành công!', 'success')
    return redirect(url_for('admin.contacts'))


# ==================== EXPORT NEWSLETTER SUBSCRIBERS ====================
@admin_bp.route('/contacts/export-newsletter')
@permission_required('view_contacts')
@feature_required('contacts')
def export_newsletter():
    """
    📥 Export danh sách newsletter subscribers ra CSV

    - Chỉ export những contact có subject='Đăng ký nhận tin'
    - Format: email, name, created_at
    """
    import csv
    from io import StringIO
    from flask import make_response
    from datetime import datetime

    subscribers = Contact.query.filter_by(subject='Đăng ký nhận tin').all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Email', 'Name', 'Subscribed Date'])

    for sub in subscribers:
        writer.writerow([
            sub.email,
            sub.name,
            sub.created_at_vn.strftime('%d/%m/%Y %H:%M')
        ])

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename=newsletter_subscribers_{datetime.now().strftime("%Y%m%d")}.csv'
    output.headers['Content-type'] = 'text/csv; charset=utf-8'

    return output
# ==================== EXPORT CONTACTS ====================
@admin_bp.route('/contacts/export-contacts')
@permission_required('view_contacts')
@feature_required('contacts')
def export_contacts():
    """
    📥 Export danh sách liên hệ (không bao gồm newsletter) ra CSV

    - Chỉ export những contact có subject != 'Đăng ký nhận tin'
    - Format: name, email, phone, subject, message, created_at, is_read
    """
    import csv
    from io import StringIO
    from flask import make_response
    from datetime import datetime

    contacts = Contact.query.filter(Contact.subject != 'Đăng ký nhận tin').order_by(Contact.created_at.desc()).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Họ tên', 'Email', 'Số điện thoại', 'Tiêu đề', 'Nội dung', 'Ngày gửi', 'Trạng thái'])

    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.email or '',
            contact.phone or '',
            contact.subject or '',
            contact.message,
            contact.created_at_vn.strftime('%d/%m/%Y %H:%M'),
            'Đã đọc' if contact.is_read else 'Chưa đọc'
        ])

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename=contacts_{datetime.now().strftime("%Y%m%d")}.csv'
    output.headers['Content-type'] = 'text/csv; charset=utf-8'

    return output