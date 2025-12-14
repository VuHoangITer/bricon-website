from app import db
from datetime import datetime


# ==================== JOB MODEL ====================
class Job(db.Model):
    """Model cho Tuyển dụng"""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)

    # Thông tin công việc
    department = db.Column(db.String(100))  # Phòng ban
    location = db.Column(db.String(200))  # Địa điểm làm việc
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract
    level = db.Column(db.String(50))  # Junior, Senior, Manager...
    salary = db.Column(db.String(100))  # Mức lương
    experience = db.Column(db.String(100))  # Kinh nghiệm yêu cầu

    description = db.Column(db.Text)  # Mô tả công việc
    requirements = db.Column(db.Text)  # Yêu cầu (dạng HTML list)
    benefits = db.Column(db.Text)  # Quyền lợi (dạng HTML list)

    deadline = db.Column(db.DateTime)  # Hạn nộp hồ sơ
    contact_email = db.Column(db.String(200))  # Email nhận CV

    is_active = db.Column(db.Boolean, default=True)
    is_urgent = db.Column(db.Boolean, default=False)  # Tuyển gấp
    view_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Job {self.title}>'

    def is_expired(self):
        """Kiểm tra đã hết hạn chưa"""
        if self.deadline:
            return datetime.utcnow() > self.deadline
        return False

    @property
    def created_at_vn(self):
        from app.utils import utc_to_vn
        return utc_to_vn(self.created_at)

    @property
    def updated_at_vn(self):
        from app.utils import utc_to_vn
        return utc_to_vn(self.updated_at)

    @property
    def deadline_vn(self):
        from app.utils import utc_to_vn
        return utc_to_vn(self.deadline) if self.deadline else None