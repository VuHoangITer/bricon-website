from app import db
from datetime import datetime


# ==================== SETTINGS MODEL ====================
class Settings(db.Model):
    """Model lưu cài đặt hệ thống (key-value)"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    group = db.Column(db.String(50), nullable=False)  # Nhóm: general, theme, seo, v.v.
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Settings {self.key}: {self.value}>'


# ==================== HELPER FUNCTIONS ====================
def get_setting(key, default=None):
    """Lấy giá trị setting từ DB"""
    setting = Settings.query.filter_by(key=key).first()
    return setting.value if setting else default


def set_setting(key, value, group='general', description=''):
    """Lưu hoặc cập nhật setting"""

    # BƯỚC 1: XỬ LÝ TUPLE TRƯỚC KHI GÁN (chỉ 1 lần duy nhất)
    if isinstance(value, tuple):
        if len(value) >= 1:
            value = str(value[0])  # Chỉ lấy URL từ tuple (filepath, metadata)
            # Optional: Lưu metadata vào description
            if len(value) > 1 and isinstance(value[1], dict):
                description += f" | Metadata: {value[1]}"
        else:
            value = str(value)

    # BƯỚC 2: ĐẢM BẢO VALUE LÀ STRING
    if not isinstance(value, str):
        value = str(value) if value is not None else ''

    # BƯỚC 3: TÌM HOẶC TẠO SETTING
    setting = Settings.query.filter_by(key=key).first()

    if setting:
        setting.value = value
        setting.group = group
        setting.description = description
    else:
        setting = Settings(key=key, value=value, group=group, description=description)
        db.session.add(setting)

    # BƯỚC 4: COMMIT
    db.session.commit()
    return setting