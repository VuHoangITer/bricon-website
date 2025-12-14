"""
⏰ Scheduler Service - Auto Publish Scheduled Posts
FIXED: Pass app instance để có app_context
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from app import db
from app.models.content import Blog
import logging
import atexit

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global
scheduler = None
_app = None  # ✅ Store app instance

# Timezone
UTC = pytz.UTC
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


def publish_scheduled_posts():
    """🚀 Publish tất cả bài viết đã đến giờ"""
    global _app

    if _app is None:
        logger.error("❌ App instance not found!")
        return

    try:
        with _app.app_context():
            now_utc = datetime.utcnow()
            now_vn = UTC.localize(now_utc).astimezone(VN_TZ)

            logger.info(f"🕐 Checking at UTC: {now_utc.strftime('%H:%M:%S')} | VN: {now_vn.strftime('%H:%M:%S')}")

            # Query bài viết cần publish
            posts = Blog.query.filter(
                Blog.status == 'scheduled',
                Blog.scheduled_at <= now_utc
            ).all()

            if not posts:
                logger.info("📭 No posts to publish")
                return

            # Publish từng bài
            published_count = 0
            for post in posts:
                try:
                    logger.info(f"📤 Publishing: {post.title} (ID: {post.id})")
                    post.publish()
                    db.session.commit()
                    published_count += 1
                    logger.info(f"✅ Published: {post.title}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"❌ Failed to publish {post.id}: {str(e)}")

            if published_count > 0:
                logger.info(f"🎉 Published {published_count} post(s)")

    except Exception as e:
        from sqlalchemy.exc import ProgrammingError
        if isinstance(e, ProgrammingError) and "does not exist" in str(e):
            logger.debug("⏭️ Skipping - database not ready")
        else:
            logger.error(f"❌ Scheduler error: {str(e)}", exc_info=True)


def init_scheduler(app):
    """Khởi tạo scheduler - FIXED VERSION"""
    global scheduler, _app

    if scheduler is not None:
        logger.warning("⚠️ Scheduler already running, skipping...")
        return

    # ✅ Store app instance
    _app = app

    try:
        logger.info("🚀 Starting scheduler...")

        # Tạo scheduler
        scheduler = BackgroundScheduler(
            daemon=True,
            timezone=UTC,
            job_defaults={
                'coalesce': False,
                'max_instances': 1
            }
        )

        # Thêm job: kiểm tra mỗi phút
        scheduler.add_job(
            func=publish_scheduled_posts,
            trigger='interval',
            minutes=1,
            id='publish_scheduled_posts',
            name='Auto-publish scheduled blog posts',
            replace_existing=True
        )

        # Start scheduler
        scheduler.start()

        # Log thành công
        now_utc = datetime.utcnow()
        now_vn = UTC.localize(now_utc).astimezone(VN_TZ)
        logger.info("✅ Scheduler started successfully!")
        logger.info(f"🕐 Current time - UTC: {now_utc.strftime('%H:%M:%S')} | VN: {now_vn.strftime('%H:%M:%S')}")
        logger.info("⏰ Scheduler will check every 1 minute")

        # Register shutdown handler
        atexit.register(lambda: shutdown_scheduler())

        # Chạy 1 lần ngay để test
        logger.info("🧪 Running initial check...")
        publish_scheduled_posts()

    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}", exc_info=True)
        scheduler = None


def shutdown_scheduler():
    """Shutdown scheduler khi app stop"""
    global scheduler
    if scheduler:
        try:
            scheduler.shutdown(wait=False)
            logger.info("⏰ Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")


def test_scheduled_posts():
    """🧪 Test function để debug"""
    global _app

    if _app is None:
        return {'error': 'App not initialized'}

    with _app.app_context():
        now_utc = datetime.utcnow()
        now_vn = UTC.localize(now_utc).astimezone(VN_TZ)

        posts = Blog.query.filter(Blog.status == 'scheduled').all()

        return {
            'now_utc': now_utc.strftime('%Y-%m-%d %H:%M:%S'),
            'now_vn': now_vn.strftime('%Y-%m-%d %H:%M:%S'),
            'scheduler_running': scheduler is not None and scheduler.running,
            'next_run_time': str(scheduler.get_job('publish_scheduled_posts').next_run_time) if scheduler and scheduler.running else None,
            'scheduled_posts': [{
                'id': p.id,
                'title': p.title,
                'scheduled_at_utc': p.scheduled_at.strftime('%Y-%m-%d %H:%M:%S') if p.scheduled_at else None,
                'scheduled_at_vn': UTC.localize(p.scheduled_at).astimezone(VN_TZ).strftime('%Y-%m-%d %H:%M:%S') if p.scheduled_at else None,
                'ready_to_publish': p.scheduled_at <= now_utc if p.scheduled_at else False
            } for p in posts]
        }