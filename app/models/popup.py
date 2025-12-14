"""
Model Popup/Banner khuyến mãi
"""
from app import db
from datetime import datetime


class Popup(db.Model):
    """Model quản lý popup/banner khuyến mãi"""
    __tablename__ = 'popups'

    id = db.Column(db.Integer, primary_key=True)

    # Nội dung - CHỈ CẦN ẢNH VÀ LINK
    image = db.Column(db.String(500), nullable=False)  # Banner image (bắt buộc)
    link = db.Column(db.String(500))  # URL redirect khi click ảnh

    # Hiển thị
    display_pages = db.Column(db.String(50), default='all')  # 'all', 'homepage', 'products'
    # ❌ BỎ position - luôn center

    # Tần suất
    frequency = db.Column(db.String(20), default='once_per_day')
    delay_seconds = db.Column(db.Integer, default=2)

    # Schedule
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Tracking
    view_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<Popup {self.id}>'

    @property
    def is_scheduled_active(self):
        """Kiểm tra popup có trong khoảng thời gian active không"""
        now = datetime.utcnow()
        if not self.start_date and not self.end_date:
            return True
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def should_display(self):
        """Check tất cả điều kiện để hiển thị popup"""
        return self.is_active and self.is_scheduled_active

    @property
    def conversion_rate(self):
        """Tỷ lệ chuyển đổi (%)"""
        if self.view_count == 0:
            return 0
        return round((self.click_count / self.view_count) * 100, 2)

    def increment_views(self):
        """Tăng số lượt xem"""
        self.view_count += 1
        db.session.commit()

    def increment_clicks(self):
        """Tăng số lượt click"""
        self.click_count += 1
        db.session.commit()

    @staticmethod
    def get_active_popup(page='all'):
        """Lấy popup active cho trang hiện tại"""
        now = datetime.utcnow()

        popup = Popup.query.filter(
            Popup.is_active == True,
            Popup.display_pages == page,
            db.or_(Popup.start_date == None, Popup.start_date <= now),
            db.or_(Popup.end_date == None, Popup.end_date >= now)
        ).order_by(Popup.created_at.desc()).first()

        if not popup:
            popup = Popup.query.filter(
                Popup.is_active == True,
                Popup.display_pages == 'all',
                db.or_(Popup.start_date == None, Popup.start_date <= now),
                db.or_(Popup.end_date == None, Popup.end_date >= now)
            ).order_by(Popup.created_at.desc()).first()

        return popup