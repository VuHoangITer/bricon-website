# File: app/main/routes/wizard.py
"""
🧙 Product Selector Wizard Routes (Public) - FINAL VERSION
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.main import main_bp
from app import db
from app.models.wizard import Wizard, WizardStep, WizardOption, WizardResult, get_wizard_with_steps
from app.models.product import Product
import uuid
import json


# ==================== WIZARD LANDING PAGE ====================
@main_bp.route('/product-wizard')
def product_wizard():
    """Trang landing chọn wizard"""
    # Clear session cũ
    session.pop('wizard_session', None)
    session.pop('wizard_id', None)
    session.pop('wizard_answers', None)

    # Tìm default wizard hoặc wizard đầu tiên
    default_wizard = Wizard.query.filter_by(is_active=True, is_default=True).first()

    if not default_wizard:
        default_wizard = Wizard.query.filter_by(is_active=True).first()

    if default_wizard:
        return redirect(url_for('main.wizard_start', wizard_id=default_wizard.id))

    # Không có wizard nào → Về trang chủ
    flash('Tính năng đang được cập nhật!', 'info')
    return redirect(url_for('main.index'))


# ==================== START WIZARD ====================
@main_bp.route('/product-wizard/<int:wizard_id>/start')
def wizard_start(wizard_id):
    """Bắt đầu wizard - KHÔNG BAO GIỜ REDIRECT VỀ PRODUCTS"""
    wizard = get_wizard_with_steps(wizard_id)

    if not wizard or not wizard.is_active:
        flash('Wizard không khả dụng!', 'warning')
        return redirect(url_for('main.index'))

    # Tạo session mới
    session['wizard_session'] = str(uuid.uuid4())
    session['wizard_id'] = wizard_id
    session['wizard_answers'] = {}

    return render_template('public/wizard/start.html', wizard=wizard)


# ==================== WIZARD STEP ====================
@main_bp.route('/product-wizard/<int:wizard_id>/step/<int:step_num>', methods=['GET', 'POST'])
def wizard_step(wizard_id, step_num):
    """Xử lý từng bước wizard"""
    wizard = get_wizard_with_steps(wizard_id)

    if not wizard or not wizard.is_active:
        flash('Wizard không khả dụng!', 'warning')
        return redirect(url_for('main.index'))

    # Check session
    if 'wizard_session' not in session or session.get('wizard_id') != wizard_id:
        flash('Phiên làm việc hết hạn. Vui lòng bắt đầu lại!', 'info')
        return redirect(url_for('main.wizard_start', wizard_id=wizard_id))

    # Lấy step hiện tại
    current_step = WizardStep.query.filter_by(
        wizard_id=wizard_id,
        step_number=step_num
    ).first()

    if not current_step:
        flash(f'Bước {step_num} không tồn tại!', 'warning')
        return redirect(url_for('main.wizard_start', wizard_id=wizard_id))

    # Load options
    options = WizardOption.query.filter_by(step_id=current_step.id) \
        .order_by(WizardOption.order).all()

    if not options:
        flash(f'Bước {step_num} chưa có lựa chọn!', 'warning')
        return redirect(url_for('main.wizard_start', wizard_id=wizard_id))

    # POST: Lưu câu trả lời
    if request.method == 'POST':
        answers = session.get('wizard_answers', {})

        if current_step.step_type == 'single_choice':
            selected = request.form.get('option')
            if selected:
                option = WizardOption.query.get(int(selected))
                if option:
                    answers[f'step_{step_num}'] = {
                        'option_id': option.id,
                        'option_text': option.option_text,
                        'tags': option.tags or []
                    }
        else:  # multiple_choice
            selected = request.form.getlist('options[]')
            if selected:
                selected_options = []
                all_tags = []
                for opt_id in selected:
                    option = WizardOption.query.get(int(opt_id))
                    if option:
                        selected_options.append({
                            'option_id': option.id,
                            'option_text': option.option_text
                        })
                        if option.tags:
                            all_tags.extend(option.tags)

                answers[f'step_{step_num}'] = {
                    'options': selected_options,
                    'tags': list(set(all_tags))
                }

        session['wizard_answers'] = answers

        # Check step tiếp theo
        next_step = WizardStep.query.filter_by(
            wizard_id=wizard_id,
            step_number=step_num + 1
        ).first()

        if next_step:
            return redirect(url_for('main.wizard_step',
                                    wizard_id=wizard_id,
                                    step_num=step_num + 1))
        else:
            # Hết steps → Kết quả
            return redirect(url_for('main.wizard_result', wizard_id=wizard_id))

    # GET: Hiển thị form
    saved_answer = session.get('wizard_answers', {}).get(f'step_{step_num}')

    # Tính progress - Safe
    total_steps = max(wizard.total_steps, 3)
    progress = int((step_num / total_steps) * 100)

    has_previous = step_num > 1

    return render_template('public/wizard/step.html',
                           wizard=wizard,
                           current_step=current_step,
                           options=options,
                           step_num=step_num,
                           total_steps=total_steps,
                           progress=progress,
                           has_previous=has_previous,
                           saved_answer=saved_answer)


# ==================== WIZARD RESULT ====================
@main_bp.route('/product-wizard/<int:wizard_id>/result')
def wizard_result(wizard_id):
    """Hiển thị kết quả"""
    wizard = Wizard.query.get_or_404(wizard_id)

    # Check session
    if 'wizard_session' not in session or session.get('wizard_id') != wizard_id:
        flash('Phiên làm việc hết hạn. Vui lòng làm lại!', 'warning')
        return redirect(url_for('main.wizard_start', wizard_id=wizard_id))

    answers = session.get('wizard_answers', {})

    if not answers:
        flash('Bạn chưa trả lời câu hỏi nào!', 'warning')
        return redirect(url_for('main.wizard_start', wizard_id=wizard_id))

    # Matching algorithm
    recommended_products = match_products_with_answers(answers)

    # Lưu kết quả
    result = WizardResult(
        wizard_id=wizard_id,
        session_id=session['wizard_session'],
        answers=answers,
        recommended_products=[{
            'product_id': p['product'].id,
            'match_score': p['score'],
            'reasons': p['reasons']
        } for p in recommended_products],
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )

    try:
        db.session.add(result)
        db.session.commit()
    except:
        pass

    return render_template('public/wizard/result.html',
                           wizard=wizard,
                           answers=answers,
                           recommended_products=recommended_products)


# ==================== RESET WIZARD ====================
@main_bp.route('/product-wizard/<int:wizard_id>/reset')
def wizard_reset(wizard_id):
    """Reset và làm lại"""
    session.pop('wizard_session', None)
    session.pop('wizard_id', None)
    session.pop('wizard_answers', None)
    flash('Đã reset! Làm lại từ đầu.', 'info')
    return redirect(url_for('main.wizard_start', wizard_id=wizard_id))


# ==================== MATCHING ALGORITHM ====================
def match_products_with_answers(answers):
    """
    Match sản phẩm với câu trả lời

    Logic:
    1. Lấy tất cả tags từ answers
    2. Query products có tags khớp
    3. Tính % match
    4. Return top 5
    """
    # Thu thập tags
    all_tags = []
    for answer in answers.values():
        if 'tags' in answer:
            all_tags.extend(answer['tags'])

    all_tags = list(set(all_tags))  # Remove duplicates

    if not all_tags:
        # Không có tags → Featured products
        products = Product.query.filter_by(is_active=True, is_featured=True).limit(5).all()
        return [{
            'product': p,
            'score': 50,
            'reasons': ['Sản phẩm nổi bật']
        } for p in products]

    # Query products
    products = Product.query.filter_by(is_active=True).all()
    scored_products = []

    for product in products:
        if not product.technical_info:
            continue

        product_tags = product.technical_info.get('tags', [])

        if not product_tags:
            # Fallback: tìm trong technical_info
            product_text = json.dumps(product.technical_info, ensure_ascii=False).lower()
            matched_tags = [tag for tag in all_tags if tag.lower() in product_text]
        else:
            matched_tags = [tag for tag in all_tags if tag in product_tags]

        if matched_tags:
            match_score = int((len(matched_tags) / len(all_tags)) * 100)

            # Dịch tags sang tiếng Việt cho reasons
            tag_vn_map = {
                'nha-o': 'Nhà ở',
                'cong-nghiep': 'Công nghiệp',
                'noi-that': 'Nội thất',
                'ngoai-that': 'Ngoại thất',
                'chong-tham': 'Chống thấm',
                'chiu-nhiet': 'Chịu nhiệt',
                'than-thien-moi-truong': 'Thân thiện môi trường',
                'chong-chay': 'Chống cháy',
                'it-mui': 'Ít mùi',
                'nhanh-kho': 'Nhanh khô'
            }

            reasons = []
            for tag in matched_tags[:3]:
                tag_display = tag_vn_map.get(tag, tag.replace('-', ' ').title())
                reasons.append(f"✓ {tag_display}")

            scored_products.append({
                'product': product,
                'score': match_score,
                'reasons': reasons
            })

    # Sort theo score
    scored_products.sort(key=lambda x: x['score'], reverse=True)

    # Không có sản phẩm match → Featured
    if not scored_products:
        products = Product.query.filter_by(is_active=True, is_featured=True).limit(5).all()
        return [{
            'product': p,
            'score': 60,
            'reasons': ['Sản phẩm được đề xuất']
        } for p in products]

    # Top 5
    return scored_products[:5]