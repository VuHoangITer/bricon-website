from flask import Blueprint

# Tạo Blueprint cho frontend
main_bp = Blueprint('main', __name__)

# Import routes sau khi khởi tạo blueprint để tránh circular import
from app.main.routes import (
    home,
    products,
    blog,
    contact,
    projects,
    careers,
    quiz,
    distributors,  # ✅ THÊM DÒNG NÀY
    misc
)