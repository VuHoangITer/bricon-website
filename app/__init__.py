from flask import Flask, g, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_compress import Compress
from flask_wtf.csrf import CSRFProtect
from app.config import Config
import cloudinary
import os
from dotenv import load_dotenv
import pytz
import time

# Khởi tạo extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
compress = Compress()
csrf = CSRFProtect()

# Timezone Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


# ===== CACHE MANAGER (GLOBAL) =====
class CacheManager:
    """Quản lý cache với TTL động từ settings"""

    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._stats = {'hits': 0, 'misses': 0, 'clears': 0}

    def get_ttl(self):
        """Lấy TTL từ settings"""
        from app.models.settings import get_setting
        try:
            return max(int(get_setting('cache_time', '300')), 0)
        except:
            return 300

    def get(self, key):
        """Lấy cache với TTL check"""
        if key not in self._cache:
            self._stats['misses'] += 1
            return None

        ttl = self.get_ttl()
        if ttl > 0:
            age = time.time() - self._timestamps.get(key, 0)
            if age > ttl:
                self.delete(key)
                self._stats['misses'] += 1
                return None

        self._stats['hits'] += 1
        return self._cache[key]

    def set(self, key, value):
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def delete(self, key):
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def clear(self, pattern=None):
        """Clear cache theo pattern hoặc tất cả"""
        if pattern:
            keys = [k for k in list(self._cache.keys()) if pattern in k]
            for k in keys:
                self.delete(k)
        else:
            self._cache.clear()
            self._timestamps.clear()
        self._stats['clears'] += 1

    def get_stats(self):
        """Thống kê cache"""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'clears': self._stats['clears'],
            'cached_keys': len(self._cache),
            'ttl_seconds': self.get_ttl(),
            'keys': list(self._cache.keys())
        }

    def is_cached(self, key):
        """Check xem key có đang cached không"""
        return self.get(key) is not None


# Global cache instance
cache_manager = CacheManager()


def create_app(config_class=Config):
    """Factory function để tạo Flask app - Tối ưu cho Render"""
    load_dotenv()
    app = Flask(__name__)

    # ==================== CONFIG ====================
    app.config.from_object(config_class)
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    app.config['CHATBOT_ENABLED'] = True

    # ===== SESSION SECURITY - Từ config class, KHÔNG override =====
    # Config class đã set SESSION_COOKIE_SECURE dựa vào môi trường
    # Development: False (HTTP OK)
    # Production: True (Chỉ HTTPS)

    # Upload Security
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Static files caching
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # ==================== INIT EXTENSIONS ====================
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)

    # ==================== CLOUDINARY ====================
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )

    # ==================== FLASK-LOGIN ====================
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'warning'

    # ==================== REGISTER BLUEPRINTS ====================
    from app.main import main_bp
    from app.admin import admin_bp
    from app.chatbot import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chatbot_bp)

    # ==================== GROQ INIT ====================
    with app.app_context():
        from app.chatbot.routes import init_groq
        init_groq()

    config_class.init_app(app)

    # ==================== CONTEXT PROCESSOR (WITH CACHE) ====================
    @app.context_processor
    def inject_globals():
        """Inject globals với cache thông minh"""
        from app.models.settings import get_setting
        from app.models.product import Category
        from app.models.features import get_feature_context
        from app.models.wizard import get_default_wizard  # ⭐ THÊM IMPORT WIZARD
        from datetime import datetime

        cached_categories = cache_manager.get('categories_active')
        if cached_categories is None:
            cached_categories = Category.query.filter_by(is_active=True).all()
            cache_manager.set('categories_active', cached_categories)

        feature_context = get_feature_context()

        return {
            'get_setting': get_setting,
            'site_name': app.config.get('SITE_NAME'),
            'all_categories': cached_categories,
            'current_year': datetime.now().year,
            'default_banner': get_setting('default_banner', ''),
            'website_name': get_setting('website_name', 'BRICON VIỆT NAM'),
            'logo_url': get_setting('logo_url', '/static/img/logo.png'),
            'hotline': get_setting('hotline', '0901.180.094'),
            'contact_email': get_setting('contact_email', 'info@bricon.vn'),
            'get_default_wizard': get_default_wizard,
            **feature_context
        }

    # ==================== POPUP INJECTION ====================
    @app.before_request
    def inject_popup():
        """Inject popup vào g để dùng trong templates"""
        from flask import g, request
        from app.models.popup import Popup

        # Chỉ inject cho frontend (không phải admin)
        if not request.path.startswith('/admin'):
            # Xác định page hiện tại
            if request.path == '/':
                page = 'homepage'
            elif request.path.startswith('/san-pham') or request.path.startswith('/products'):
                page = 'products'
            elif request.path.startswith('/tin-tuc') or request.path.startswith('/blogs'):
                page = 'blogs'
            elif request.path.startswith('/lien-he') or request.path.startswith('/contact'):
                page = 'contact'
            else:
                page = 'all'

            # Lấy popup active
            g.popup = Popup.get_active_popup(page)

    # ==================== JINJA2 FILTERS ====================
    @app.template_filter('format_price')
    def format_price(value):
        if value:
            return '{:,.0f}'.format(value).replace(',', '.')
        return '0'

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if not text:
            return ''
        return text.replace('\n', '<br>\n')

    # ==================== TIMEZONE FILTERS ====================
    @app.template_filter('vn_datetime')
    def vn_datetime_filter(dt, format='%d/%m/%Y %H:%M:%S'):
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        vn_dt = dt.astimezone(VN_TZ)
        return vn_dt.strftime(format)

    @app.template_filter('vn_date')
    def vn_date_filter(dt):
        return vn_datetime_filter(dt, '%d/%m/%Y')

    @app.template_filter('vn_time')
    def vn_time_filter(dt):
        return vn_datetime_filter(dt, '%H:%M:%S')

    @app.template_filter('vn_datetime_friendly')
    def vn_datetime_friendly_filter(dt):
        return vn_datetime_filter(dt, '%d/%m/%Y lúc %H:%M')

    # ==================== ERROR HANDLERS ====================
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(502)
    @app.errorhandler(503)
    def service_unavailable(error):
        return render_template('errors/500.html'), 503

    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash('File quá lớn! Kích thước tối đa là 16MB.', 'danger')
        return redirect(url_for('main.index'))

    @app.after_request
    def after_request(response):
        # Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # HSTS - Chỉ bật khi đang dùng HTTPS
        if request.is_secure or os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        is_admin = request.path.startswith('/admin')

        # CSP - Chỉ bật cho production + non-admin pages
        if os.getenv('FLASK_ENV') == 'production' and not is_admin:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com https://www.googletagmanager.com https://cdnjs.cloudflare.com https://www.google-analytics.com https://connect.facebook.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
                "img-src 'self' data: https: http: blob:",
                "connect-src 'self' https://www.google-analytics.com https://res.cloudinary.com https://cdn.jsdelivr.net https://www.facebook.com",
                "frame-src 'self' https://www.youtube.com https://www.google.com https://www.facebook.com",
                "media-src 'self' https: data:",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'self'",
                "upgrade-insecure-requests"
            ]
            response.headers['Content-Security-Policy'] = "; ".join(csp_directives)

        return response

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # ==================== CUSTOM CLI COMMANDS ====================
    @app.cli.command()
    def clear_cache():
        """Clear all cache"""
        cache_manager.clear()
        print("Cache cleared successfully!")

    @app.cli.command()
    def cache_stats():
        """Show cache statistics"""
        stats = cache_manager.get_stats()
        print("\nCache Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    @app.cli.command()
    def test_security():
        """Test security headers"""
        with app.test_client() as client:
            response = client.get('/')
            print("\nSecurity Headers Check:")
            headers_to_check = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Referrer-Policy',
                'Permissions-Policy',
                'Content-Security-Policy'
            ]
            for header in headers_to_check:
                value = response.headers.get(header, 'NOT SET')
                print(f"  {header}: {value}")

    # ==================== SCHEDULER INIT (AUTO PUBLISH POSTS) ====================
    if app.config.get('SCHEDULER_ENABLED', True) and os.getenv('ENABLE_SCHEDULER', '1') == '1':
        try:
            from app.scheduler import init_scheduler
            init_scheduler(app)
            app.logger.info("✅ Scheduler enabled for this worker")
        except Exception as e:
            app.logger.error(f"❌ Failed to init scheduler: {str(e)}")
    else:
        if app.config.get('SCHEDULER_ENABLED', True):
            app.logger.info("⏭️ Scheduler disabled for this worker (ENABLE_SCHEDULER=0)")


    return app

# ==================== USER LOADER ====================
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from app.models.user import User
    return User.query.get(int(user_id))