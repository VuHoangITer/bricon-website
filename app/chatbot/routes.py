from flask import request, jsonify, session, current_app
from . import chatbot_bp
from datetime import datetime
import json
import os
from app.models.features import feature_required
from groq import Groq

# ==================== GLOBALS ====================
groq_client = None
_COMPANY_INFO_CACHE = None
_COMPANY_INFO_MTIME = None
_DEFAULT_MODEL_NAME = 'llama-3.3-70b-versatile'


# ==================== INIT GROQ ====================
def init_groq():
    """Khởi tạo Groq API (được gọi khi app boot và khi lần đầu /send)."""
    global groq_client
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        current_app.logger.warning("⚠️ GROQ_API_KEY not found in config")
        groq_client = None
        return

    try:
        groq_client = Groq(api_key=api_key)
        current_app.logger.info("✅ Groq API initialized successfully")
    except Exception as e:
        current_app.logger.error(f"❌ Failed to initialize Groq API: {str(e)}")
        groq_client = None


# ==================== COMPANY INFO (CACHE + INVALIDATION) ====================
def load_company_info():
    """
    Đọc company_info.json với cache theo mtime:
    - Lần đầu: đọc file & cache
    - Khi file đổi (mtime khác): reload
    - Nếu lỗi, trả về cache cũ (nếu có) để không gián đoạn
    """
    global _COMPANY_INFO_CACHE, _COMPANY_INFO_MTIME
    json_path = os.path.join(current_app.root_path, 'chatbot', 'company_info.json')

    try:
        mtime = os.path.getmtime(json_path)
        if _COMPANY_INFO_CACHE is not None and _COMPANY_INFO_MTIME == mtime:
            return _COMPANY_INFO_CACHE

        with open(json_path, 'r', encoding='utf-8') as f:
            _COMPANY_INFO_CACHE = json.load(f)
            _COMPANY_INFO_MTIME = mtime
            current_app.logger.info(f"✅ Loaded company info (mtime={mtime})")
            return _COMPANY_INFO_CACHE
    except FileNotFoundError:
        current_app.logger.error(f"❌ company_info.json not found at {json_path}")
        return _COMPANY_INFO_CACHE or {}
    except json.JSONDecodeError as e:
        current_app.logger.error(f"❌ Invalid JSON: {str(e)}")
        return _COMPANY_INFO_CACHE or {}
    except Exception as e:
        current_app.logger.error(f"❌ load_company_info error: {str(e)}")
        return _COMPANY_INFO_CACHE or {}


# ==================== FULL PROMPT (LUÔN DÙNG) ====================
def create_full_prompt(company_info: dict) -> str:
    """
    Tạo prompt FULL với toàn bộ thông tin từ JSON
    Không cắt giảm, không summarize
    """
    # Thông tin cơ bản
    company_name = company_info.get('company_name', 'CÔNG TY TNHH BRICON VIỆT NAM')
    slogan = company_info.get('slogan', 'Kết dính bền lâu – Xây dựng niềm tin')
    company_intro = company_info.get('company_intro', '')

    contact = company_info.get('contact', {}) or {}
    phone = contact.get('phone', '0901.180.094')
    hotline = contact.get('hotline', '0901180094')
    email = contact.get('email', 'info@bricon.vn')
    zalo = contact.get('zalo', phone)
    address = contact.get('address', '171 Đường An Phú Đông 03, P. An Phú Đông, Q.12, TP.HCM')
    website = contact.get('website', 'https://www.bricon.vn')
    working_hours = contact.get('working_hours', '8:00 - 17:30 (Thứ 2 - Thứ 7)')

    # Chi nhánh
    branches = contact.get('branches', []) or []
    branches_text = "\n".join([
        f"• {b.get('name', 'N/A')}: {b.get('address', 'N/A')}"
        for b in branches
    ]) or "—"

    # TOÀN BỘ SẢN PHẨM - KHÔNG CẮT GIẢM
    products = company_info.get('products', []) or []
    products_list = []
    for p in products:
        info = []
        info.append(f"━━━ {p.get('name', 'N/A')} ━━━")
        if p.get('category'):
            info.append(f"• Loại: {p['category']}")
        if p.get('brand'):
            info.append(f"• Thương hiệu: {p['brand']}")
        if p.get('description'):
            info.append(f"• Mô tả: {p['description']}")

        # Composition
        if p.get('composition'):
            info.append("• Thành phần:")
            for comp in p['composition']:
                info.append(f"  - {comp}")

        # Application
        if p.get('application'):
            info.append("• Ứng dụng:")
            for app in p['application']:
                info.append(f"  - {app}")

        # Technical specs (FULL - không cắt)
        if p.get('technical_specs'):
            info.append("• Thông số kỹ thuật:")
            for k, v in p['technical_specs'].items():
                info.append(f"  - {k}: {v}")

        if p.get('packaging'):
            info.append(f"• Đóng gói: {p['packaging']}")
        if p.get('colors'):
            info.append(f"• Màu sắc: {', '.join(p['colors'])}")
        if p.get('expiry'):
            info.append(f"• Hạn sử dụng: {p['expiry']}")
        if p.get('standards'):
            info.append(f"• Tiêu chuẩn: {p['standards']}")

        products_list.append("\n".join(info))

    products_text = "\n\n".join(products_list) or "—"

    # Ưu điểm
    strengths = company_info.get('strengths', []) or []
    strengths_text = "\n".join([f"✓ {s}" for s in strengths]) or "—"

    # Chính sách đổi trả
    rp = company_info.get('return_policy', {}) or {}
    return_summary = rp.get('policy_summary', 'Công ty có chính sách đổi trả linh hoạt')
    conditions = rp.get('conditions', {}) or {}
    conditions_parts = []
    for key, value in conditions.items():
        if isinstance(value, list):
            items = "\n".join([f"  • {item}" for item in value])
            conditions_parts.append(f"\n{key}:\n{items}")
        else:
            conditions_parts.append(f"\n{key}: {value}")
    conditions_text = "".join(conditions_parts)

    notes = rp.get('note', []) or []
    notes_text = "\n".join([f"⚠️ {n}" for n in notes]) if notes else ""

    # Quy trình đặt hàng
    process = company_info.get('process', []) or []
    process_text = "\n".join([f"{i + 1}. {s}" for i, s in enumerate(process)]) or "—"

    # Dự án (TOÀN BỘ - không giới hạn 15)
    projects = company_info.get('projects', []) or []
    projects_text = "\n".join([f"• {proj}" for proj in projects]) or "—"

    # FAQ (TOÀN BỘ - không cắt)
    faq = company_info.get('faq', []) or []
    faq_text = "\n".join([
        f"❓ {q.get('question', '')}\n💡 {q.get('answer', '')}\n"
        for q in faq
    ]) or "—"

    return f"""BẠN LÀ TRỢ LÝ ẢO BRICON - CHUYÊN GIA VẬT LIỆU XÂY DỰNG

🏢 {company_name} | 💡 {slogan}
📞 {hotline} | 💬 Zalo: {zalo} | 📧 {email} | 🌐 {website}
📍 {address} | ⏰ {working_hours}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 GIỚI THIỆU CÔNG TY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{company_intro}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏪 HỆ THỐNG CHI NHÁNH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{branches_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 DANH MỤC SẢN PHẨM CHI TIẾT (TOÀN BỘ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{products_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ ƯU ĐIỂM NỔI BẬT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{strengths_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 CHÍNH SÁCH ĐỔI TRẢ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 {return_summary}
✅ Điều kiện:{conditions_text}
{notes_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 QUY TRÌNH ĐẶT HÀNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{process_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏗️ DỰ ÁN TIÊU BIỂU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{projects_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ CÂU HỎI THƯỜNG GẶP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{faq_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NGUYÊN TẮC TRẢ LỜI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Trả lời CHÍNH XÁC dựa trên thông tin đã cung cấp ở trên
2. Trích dẫn cụ thể từ phần sản phẩm/FAQ khi được hỏi về thông số kỹ thuật
3. KHÔNG đưa giá cụ thể → hướng dẫn liên hệ {hotline} hoặc Zalo {zalo}
4. Thân thiện, chuyên nghiệp, ngắn gọn (2-5 câu)
5. Nếu không chắc chắn → nói thẳng và cho thông tin liên hệ
6. Ưu tiên câu trả lời ngắn gọn, tránh dài dòng trừ khi khách yêu cầu chi tiết
7. Luôn trả lời bằng tiếng Việt có dấu
8. Khi khách hỏi về sản phẩm → giới thiệu sản phẩm phù hợp nhất từ danh mục
"""


# ==================== PROMPT BUILDER ====================
def build_messages(system_prompt: str, history_context: str, user_message: str) -> list:
    """Tạo messages array cho Groq API"""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Thêm lịch sử hội thoại nếu có
    if history_context:
        messages.append({
            "role": "user",
            "content": f"Lịch sử hội thoại:\n{history_context}"
        })

    # Thêm tin nhắn hiện tại
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages


# ==================== ROUTES ====================
@chatbot_bp.route('/send', methods=['POST'])
@feature_required('chatbot')
def send_message():
    """
    Xử lý tin nhắn với Groq - LUÔN DÙNG FULL MODE
    """
    global groq_client

    # Bật/tắt chatbot
    if not current_app.config.get('CHATBOT_ENABLED', True):
        return jsonify({'response': '⚠️ Chatbot đang bảo trì. Vui lòng liên hệ: 📞 0901 180 094'}), 503

    # Init client nếu chưa có
    if groq_client is None:
        init_groq()
    if groq_client is None:
        return jsonify({'response': '😔 Chatbot tạm thời không khả dụng.\nLiên hệ: 📞 0901180094'}), 500

    try:
        data = request.json or {}
        user_message = (data.get('message') or '').strip()

        # Validate
        if not user_message:
            return jsonify({'error': 'Tin nhắn không được để trống'}), 400
        if len(user_message) > 500:
            return jsonify({'error': 'Tin nhắn quá dài (tối đa 500 ký tự)'}), 400

        # Rate limit theo session
        if 'chatbot_request_count' not in session:
            session['chatbot_request_count'] = 0
            session['chatbot_request_start_time'] = datetime.now().timestamp()

        now_ts = datetime.now().timestamp()
        request_limit = int(current_app.config.get('CHATBOT_REQUEST_LIMIT', 15))
        window = int(current_app.config.get('CHATBOT_REQUEST_WINDOW', 3600))  # 1h

        # Reset window
        if now_ts - session['chatbot_request_start_time'] > window:
            session['chatbot_request_count'] = 0
            session['chatbot_request_start_time'] = now_ts

        if session['chatbot_request_count'] >= request_limit:
            return jsonify({
                'response': (
                    f'⏰ Anh/chị đã dùng hết {request_limit} lượt chat/giờ.\n'
                    f'Vui lòng thử lại sau hoặc liên hệ 📞 0901.180.094 | Zalo {current_app.config.get("HOTLINE_ZALO", "0901.180.094")}'
                )
            })

        session['chatbot_request_count'] += 1

        # Lịch sử hội thoại (tăng lên 10 turns để nhớ lâu hơn)
        history_turns = int(current_app.config.get('CHATBOT_HISTORY_TURNS', 10))
        if 'chatbot_history' not in session:
            session['chatbot_history'] = []
        history_context = "\n".join([
            f"{'Khách' if msg['role'] == 'user' else 'Bot'}: {msg['content']}"
            for msg in session['chatbot_history'][-history_turns:]
        ])

        # Tạo FULL PROMPT (luôn luôn)
        company_info = load_company_info()
        system_prompt = create_full_prompt(company_info)
        messages = build_messages(system_prompt, history_context, user_message)

        # Gọi Groq API
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model=current_app.config.get('GROQ_MODEL', _DEFAULT_MODEL_NAME),
                temperature=0.4,  # Giảm xuống 0.4 để ổn định hơn
                max_tokens=1000,  # Tăng lên 1000 vì full mode
                top_p=0.9,
                stream=False
            )

            bot_reply = chat_completion.choices[0].message.content.strip()

            if not bot_reply:
                bot_reply = (
                    "😔 Dạ xin lỗi, em chưa có đủ thông tin để trả lời.\n"
                    "Anh/chị vui lòng liên hệ: 📞 0901180094 hoặc Zalo 0901.180.094 để được hỗ trợ nhanh ạ."
                )

        except Exception as api_error:
            current_app.logger.error(f"❌ Groq API error: {str(api_error)}")
            return jsonify({
                'response': '⚠️ Hệ thống đang quá tải, anh/chị vui lòng thử lại sau vài giây hoặc gọi 📞 0901180094.'
            }), 500

        # Lưu lịch sử (tăng lên 30 message)
        session['chatbot_history'].append({'role': 'user', 'content': user_message})
        session['chatbot_history'].append({'role': 'assistant', 'content': bot_reply})
        session['chatbot_history'] = session['chatbot_history'][-30:]
        session.modified = True

        remaining = request_limit - session['chatbot_request_count']

        return jsonify({
            'response': bot_reply,
            'mode': 'full',  # Luôn là full
            'remaining_requests': remaining,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"❌ Chatbot error: {str(e)}", exc_info=True)
        return jsonify({
            'response': '😔 Đã có lỗi xảy ra. Vui lòng liên hệ BRICON: 📞 0901180094 | Zalo 0901.180.094 | Email info@bricon.vn'
        }), 500


@chatbot_bp.route('/reset', methods=['POST'])
@feature_required('chatbot')
def reset_chat():
    """Xoá lịch sử + đếm lượt"""
    try:
        session.pop('chatbot_history', None)
        session.pop('chatbot_request_count', None)
        session.pop('chatbot_request_start_time', None)
        session.modified = True
        current_app.logger.info("✅ Chat history reset successfully")
        return jsonify(
            {'status': 'success', 'message': '✅ Đã làm mới hội thoại', 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        current_app.logger.error(f"❌ Reset chat error: {str(e)}")
        return jsonify({'status': 'error', 'message': '⚠️ Không thể làm mới hội thoại'}), 500


@chatbot_bp.route('/status', methods=['GET'])
@feature_required('chatbot')
def chatbot_status():
    """Kiểm tra trạng thái chatbot"""
    try:
        global groq_client
        limit = int(current_app.config.get('CHATBOT_REQUEST_LIMIT', 15))
        used = int(session.get('chatbot_request_count', 0))
        return jsonify({
            'enabled': current_app.config.get('CHATBOT_ENABLED', True),
            'model_initialized': groq_client is not None,
            'model': current_app.config.get('GROQ_MODEL', _DEFAULT_MODEL_NAME),
            'mode': 'full',  # Luôn là full
            'request_limit': limit,
            'remaining_requests': max(0, limit - used),
            'history_length': len(session.get('chatbot_history', [])),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"❌ Status check error: {str(e)}")
        return jsonify({'error': 'Unable to check status'}), 500


# ==================== APP HOOK ====================
def init_chatbot(app):
    """Gọi ở __init__.py khi khởi động app"""
    with app.app_context():
        init_groq()
        # Preload company info để cache sẵn
        try:
            load_company_info()
            current_app.logger.info("🤖 BRICON Chatbot initialized with Groq (FULL MODE ONLY)")
        except Exception:
            pass