# File: app/models/wizard.py

from app import db
from datetime import datetime
from sqlalchemy import event


# ==================== WIZARD MODEL ====================
class Wizard(db.Model):
    """Model chính cho Product Selector Wizard"""
    __tablename__ = 'wizards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100), default='bi-magic')  # Bootstrap icon class
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)  # Wizard mặc định hiện ở homepage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = db.relationship('WizardStep', backref='wizard', lazy='dynamic',
                            cascade='all, delete-orphan', order_by='WizardStep.step_number')
    results = db.relationship('WizardResult', backref='wizard', lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Wizard {self.name}>'

    @property
    def total_steps(self):
        """Tổng số bước"""
        return self.steps.count()

    @property
    def total_results(self):
        """Tổng số lượt sử dụng"""
        return self.results.count()


# ==================== WIZARD STEP MODEL ====================
class WizardStep(db.Model):
    """Model các bước trong wizard"""
    __tablename__ = 'wizard_steps'

    id = db.Column(db.Integer, primary_key=True)
    wizard_id = db.Column(db.Integer, db.ForeignKey('wizards.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    question_text = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)  # Mô tả thêm cho câu hỏi
    step_type = db.Column(db.String(50), default='single_choice')
    # step_type: 'single_choice', 'multiple_choice'
    is_required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    options = db.relationship('WizardOption', backref='step', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='WizardOption.order')

    def __repr__(self):
        return f'<WizardStep {self.step_number}: {self.question_text[:30]}>'

    @property
    def total_options(self):
        """Tổng số lựa chọn"""
        return self.options.count()


# ==================== WIZARD OPTION MODEL ====================
class WizardOption(db.Model):
    """Model các lựa chọn cho mỗi bước"""
    __tablename__ = 'wizard_options'

    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(db.Integer, db.ForeignKey('wizard_steps.id'), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))  # Mô tả ngắn
    icon_class = db.Column(db.String(100))  # Bootstrap icon: 'bi-house-fill'
    emoji = db.Column(db.String(10))  # Emoji: '🏠', '🌳'
    tags = db.Column(db.JSON)  # Tags để match với products
    # Ví dụ: ["interior", "residential", "waterproof"]
    order = db.Column(db.Integer, default=0)  # Thứ tự hiển thị
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WizardOption {self.option_text}>'


# ==================== WIZARD RESULT MODEL ====================
class WizardResult(db.Model):
    """Model lưu kết quả wizard của user"""
    __tablename__ = 'wizard_results'

    id = db.Column(db.Integer, primary_key=True)
    wizard_id = db.Column(db.Integer, db.ForeignKey('wizards.id'), nullable=False)
    session_id = db.Column(db.String(100))  # Session ID của user (không cần login)
    user_email = db.Column(db.String(255))  # Optional: nếu user muốn nhận kết quả

    # Lưu câu trả lời của user dạng JSON
    answers = db.Column(db.JSON, nullable=False)
    # Ví dụ: {
    #   "step_1": {"option_id": 1, "option_text": "Nhà ở dân dụng"},
    #   "step_2": {"option_ids": [3, 5], "option_texts": ["Chống thấm", "Nhanh khô"]}
    # }

    # Lưu sản phẩm được gợi ý dạng JSON
    recommended_products = db.Column(db.JSON)
    # Ví dụ: [
    #   {"product_id": 5, "match_score": 85, "reasons": ["Chống thấm", "Dùng ngoài trời"]},
    #   {"product_id": 12, "match_score": 80, "reasons": [...]}
    # ]

    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WizardResult {self.id} - Wizard {self.wizard_id}>'


# ==================== AUTO CLEAR CACHE EVENTS ====================

@event.listens_for(Wizard, 'after_insert')
@event.listens_for(Wizard, 'after_update')
@event.listens_for(Wizard, 'after_delete')
def clear_wizard_cache(mapper, connection, target):
    from app import cache_manager
    cache_manager.clear('wizards')


@event.listens_for(WizardStep, 'after_insert')
@event.listens_for(WizardStep, 'after_update')
@event.listens_for(WizardStep, 'after_delete')
def clear_wizard_step_cache(mapper, connection, target):
    from app import cache_manager
    cache_manager.clear('wizards')
    cache_manager.clear(f'wizard_{target.wizard_id}')


@event.listens_for(WizardOption, 'after_insert')
@event.listens_for(WizardOption, 'after_update')
@event.listens_for(WizardOption, 'after_delete')
def clear_wizard_option_cache(mapper, connection, target):
    from app import cache_manager
    cache_manager.clear('wizards')
    step = WizardStep.query.get(target.step_id)
    if step:
        cache_manager.clear(f'wizard_{step.wizard_id}')


# ==================== HELPER FUNCTIONS ====================

def get_active_wizards():
    """Lấy tất cả wizards đang active"""
    from app import cache_manager
    cached = cache_manager.get('wizards_active')
    if cached is not None:
        return cached

    wizards = Wizard.query.filter_by(is_active=True).all()
    cache_manager.set('wizards_active', wizards)
    return wizards


def get_default_wizard():
    """Lấy wizard mặc định"""
    from app import cache_manager
    cached = cache_manager.get('wizard_default')
    if cached is not None:
        return cached

    wizard = Wizard.query.filter_by(is_active=True, is_default=True).first()
    cache_manager.set('wizard_default', wizard)
    return wizard


def get_wizard_with_steps(wizard_id):
    """Lấy wizard kèm theo tất cả steps và options"""
    from app import cache_manager
    cache_key = f'wizard_full_{wizard_id}'
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return cached

    wizard = Wizard.query.get(wizard_id)
    if wizard:
        # Force load relationships
        _ = wizard.steps.all()
        for step in wizard.steps:
            _ = step.options.all()
        cache_manager.set(cache_key, wizard)
    return wizard