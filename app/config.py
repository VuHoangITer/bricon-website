import os
from dotenv import load_dotenv
import time

load_dotenv()


class Config:
    """Config tối ưu cho Render Starter (512MB RAM, 0.5 CPU) — đồng bộ Gunicorn"""

    # ===== CƠ BẢN =====
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # ===== DATABASE =====
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../app.db')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===== ĐỒNG BỘ THREADS/POOL VỚI GUNICORN =====
    THREADS = int(os.environ.get('GTHREADS', 3))
    POOL_PER_WORKER = int(os.environ.get('DB_POOL_PER_WORKER', min(THREADS, 3)))
    MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 1))

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': POOL_PER_WORKER,
        'max_overflow': MAX_OVERFLOW,
        'pool_recycle': 600,
        'pool_pre_ping': True,
        'pool_timeout': 20,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'briconvn_app',
            'options': '-c statement_timeout=45000'
        },
        'echo_pool': os.environ.get('FLASK_ENV') == 'development'
    }

    # ===== UPLOAD =====
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'}

    # ===== GROQ CHATBOT =====
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')  # hoặc 'mixtral-8x7b-32768'
    CHATBOT_ENABLED = True
    CHATBOT_REQUEST_LIMIT = int(os.environ.get('CHATBOT_REQUEST_LIMIT', 15))
    CHATBOT_REQUEST_WINDOW = int(os.environ.get('CHATBOT_REQUEST_WINDOW', 3600))
    GROQ_TIMEOUT = int(os.environ.get('GROQ_TIMEOUT', 30))

    CHATBOT_HISTORY_TURNS = int(os.environ.get('CHATBOT_HISTORY_TURNS', 5))
    CHATBOT_PROMPT_MODE_DEFAULT = os.environ.get('CHATBOT_PROMPT_MODE_DEFAULT', 'lite')
    CHATBOT_TEMPERATURE = float(os.environ.get('CHATBOT_TEMPERATURE', 0.6))
    CHATBOT_MAX_OUTPUT_TOKENS = int(os.environ.get('CHATBOT_MAX_OUTPUT_TOKENS', 800))
    HOTLINE_ZALO = os.environ.get('HOTLINE_ZALO', '0901.180.094')

    # ===== SCHEDULER (AUTO PUBLISH) =====
    SCHEDULER_ENABLED = os.environ.get('SCHEDULER_ENABLED', 'true').lower() == 'true'
    SCHEDULER_CHECK_INTERVAL = int(os.environ.get('SCHEDULER_CHECK_INTERVAL', 1))  # Minutes

    # ===== FLASK-COMPRESS =====
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    # ===== CACHING =====
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # ===== SECURITY / RATE LIMIT =====
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'

    # ===== SESSION SECURITY (Mặc định FALSE cho development) =====
    SESSION_COOKIE_SECURE = False  # ← THAY ĐỔI: Mặc định False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800

    @staticmethod
    def init_app(app):
        import logging
        from logging.handlers import RotatingFileHandler
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/briconvn.log',
                maxBytes=512 * 1024,
                backupCount=2
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.ERROR)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.ERROR)
            app.logger.info('Briconvn startup')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = False  # ← Development: HTTP OK


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True  # ← Production: Chỉ HTTPS
    GEMINI_TIMEOUT = int(os.environ.get('GEMINI_TIMEOUT', 30))

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging, sys
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.ERROR)
        app.logger.addHandler(stream_handler)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}