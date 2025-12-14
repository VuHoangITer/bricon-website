from app import db
from datetime import datetime


# ==================== CONTACT MODEL ====================
class Contact(db.Model):
    """Model lưu thông tin liên hệ từ khách hàng"""
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name} - {self.email}>'

    @property
    def created_at_vn(self):
        """Lấy created_at theo múi giờ Việt Nam"""
        from app.utils import utc_to_vn
        return utc_to_vn(self.created_at)