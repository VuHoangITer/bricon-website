from flask import render_template, request, flash, redirect, url_for, jsonify
from app.main import main_bp
from app import db
from app.models.contact import Contact
from app.forms.contact import ContactForm
import re


@main_bp.route('/lien-he', methods=['GET', 'POST'])
def contact():
    """Trang liên hệ"""
    form = ContactForm()

    if form.validate_on_submit():
        # Tạo contact mới
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )

        db.session.add(contact)
        db.session.commit()

        flash('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('public/contact.html', form=form)


# ==================== NEWSLETTER SUBSCRIPTION ====================
@main_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """
    📧 Xử lý đăng ký newsletter - lưu vào bảng Contact

    - Sử dụng chung bảng Contact
    - Đánh dấu bằng subject='Đăng ký nhận tin'
    - Trả về JSON cho AJAX request
    """
    try:
        # Lấy data từ request
        data = request.get_json() if request.is_json else request.form

        email = data.get('email', '').strip().lower()
        consent_value = data.get('consent')
        consent = consent_value is True or str(consent_value).lower() == 'true'

        # Validation email
        if not email:
            return jsonify({
                'success': False,
                'message': 'Vui lòng nhập email!'
            }), 400

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({
                'success': False,
                'message': 'Email không hợp lệ!'
            }), 400

        # Check consent
        if not consent:
            return jsonify({
                'success': False,
                'message': 'Vui lòng đồng ý nhận email marketing!'
            }), 400

        # Kiểm tra email đã đăng ký newsletter chưa
        existing = Contact.query.filter_by(
            email=email,
            subject='Đăng ký nhận tin'
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'message': 'Email này đã đăng ký nhận tin từ trước!'
            }), 409

        # Tạo contact mới với subject đặc biệt
        contact = Contact(
            name='Newsletter Subscriber',
            email=email,
            phone='',  # Không có phone
            subject='Đăng ký nhận tin',  # Đánh dấu đây là newsletter
            message=f'Khách hàng đăng ký nhận bản tin và ưu đãi qua email.\nĐồng ý nhận email marketing: Có'
        )

        db.session.add(contact)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công! Bạn sẽ nhận được email xác nhận sớm.'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Newsletter subscription error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Có lỗi xảy ra. Vui lòng thử lại sau!'
        }), 500