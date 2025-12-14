"""
🔐 Authentication Routes
- Login với lockout mechanism (30 phút sau N lần sai)
- Logout
- Check Lockout API

📌 Không yêu cầu permissions (public routes trong admin)
"""

from datetime import datetime, timedelta
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.models.settings import get_setting
from app.forms.auth import LoginForm
from app.admin import admin_bp

# ==================== LOGIN & LOGOUT ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập admin - CÓ GIỚI HẠN ATTEMPTS VÀ KHÓA NẾU MÀY SAI HAHAHAAHAH"""
    if current_user.is_authenticated:
        if current_user.has_any_permission('manage_users', 'manage_products', 'manage_categories'):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('admin.welcome'))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        max_attempts = int(get_setting('login_attempt_limit', '5'))

        # Keys cho session
        attempt_key = f'login_attempts_{email}'
        lockout_key = f'login_lockout_{email}'

        # Lấy thông tin attempts và lockout time
        attempts = session.get(attempt_key, 0)
        lockout_until = session.get(lockout_key)

        # ✅ KIỂM TRA THỜI GIAN KHÓA
        if lockout_until:
            lockout_time = datetime.fromisoformat(lockout_until)
            now = datetime.now()

            if now < lockout_time:
                # Tính thời gian còn lại
                remaining_time = lockout_time - now
                minutes = int(remaining_time.total_seconds() / 60)
                seconds = int(remaining_time.total_seconds() % 60)

                flash(f'🔒 Tài khoản đang bị khóa! Vui lòng thử lại sau {minutes} phút {seconds} giây.', 'danger')
                return render_template('admin/auth/login.html', form=form)
            else:
                # Hết thời gian khóa - reset
                session.pop(attempt_key, None)
                session.pop(lockout_key, None)
                attempts = 0

        # ✅ KIỂM TRA ĐĂNG NHẬP
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            # Đăng nhập thành công - reset attempts
            login_user(user, remember=form.remember_me.data)
            session.pop(attempt_key, None)
            session.pop(lockout_key, None)

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.has_any_permission('manage_users', 'manage_products', 'manage_categories'):
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('admin.welcome'))
        else:
            # ❌ ĐĂNG NHẬP SAI
            attempts += 1
            session[attempt_key] = attempts
            remaining = max_attempts - attempts

            # ✅ HẾT LƯỢT THỬ - KHÓA 30 PHÚT
            if attempts >= max_attempts:
                lockout_time = datetime.now() + timedelta(minutes=30)
                session[lockout_key] = lockout_time.isoformat()

                flash(f'Tài khoản đã bị khóa 30 phút do đăng nhập sai {max_attempts} lần liên tiếp!', 'danger')
                return render_template('admin/auth/login.html', form=form)

            # ⚠️ CẢNH BÁO LẦN CUỐI CÙNG
            elif remaining == 1:
                flash(
                    f'⚠CẢNH BÁO: Email hoặc mật khẩu không đúng! Đây là lần thử cuối cùng. Tài khoản sẽ bị khóa 30 phút nếu nhập sai.',
                    'danger')

            # ℹ️ CÒN NHIỀU LƯỢT
            else:
                flash(f'Email hoặc mật khẩu không đúng! Còn {remaining} lần thử.', 'warning')

    return render_template('admin/auth/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    """Đăng xuất - KHÔNG CẦN QUYỀN ĐẶC BIỆT"""
    logout_user()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('admin.login'))


# ✅ ROUTE KIỂM TRA THỜI GIAN KHÓA (Optional - để user kiểm tra)
@admin_bp.route('/check-lockout', methods=['POST'])
def check_lockout():
    """API kiểm tra thời gian còn lại của lockout"""
    email = request.json.get('email')

    if not email:
        return jsonify({'locked': False})

    lockout_key = f'login_lockout_{email}'
    lockout_until = session.get(lockout_key)

    if lockout_until:
        lockout_time = datetime.fromisoformat(lockout_until)
        now = datetime.now()

        if now < lockout_time:
            remaining = int((lockout_time - now).total_seconds())
            return jsonify({
                'locked': True,
                'remaining_seconds': remaining,
                'lockout_until': lockout_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    return jsonify({'locked': False})