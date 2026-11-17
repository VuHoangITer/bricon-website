"""
Chốt (nộp hộ) các lượt làm bài bị bỏ dở, để HR xem được trong Admin > Kết quả.

Dùng khi người làm bài không nộp được (mất kết nối, lỗi phiên, đóng trình duyệt...).
Chỉ xử lý lượt chưa nộp đã quá thời gian làm bài của đề + 10 phút.
Câu trả lời đã lưu được giữ nguyên; điểm tính trên các câu đã lưu.

Chạy:
    python finalize_quiz_attempts.py           # chỉ liệt kê, KHÔNG thay đổi gì
    python finalize_quiz_attempts.py --apply   # chốt các lượt trong danh sách
"""
import sys
from datetime import datetime, timedelta

from app import create_app, db
from app.models.quiz import QuizAttempt, UserAnswer

GRACE = timedelta(minutes=10)


def main(apply=False):
    now = datetime.utcnow()
    pending = []
    for a in QuizAttempt.query.filter_by(is_completed=False).order_by(QuizAttempt.started_at).all():
        if not a.started_at or not a.quiz:
            continue
        deadline = a.started_at + timedelta(minutes=a.quiz.duration_minutes)
        if now > deadline + GRACE:
            pending.append((a, deadline))

    if not pending:
        print('Không có lượt làm bài nào bị bỏ dở.')
        return

    print(f'{"ID":>5}  {"Bắt đầu (UTC)":16}  {"Đã lưu":>6}  Người làm – Đề')
    for a, _ in pending:
        print(f'{a.id:>5}  {a.started_at:%Y-%m-%d %H:%M}  {a.user_answers.count():>6}  {a.user_name} – {a.quiz.title}')

    if not apply:
        print(f'\n{len(pending)} lượt chưa nộp. Chạy lại với --apply để chốt.')
        return

    for a, deadline in pending:
        last = db.session.query(db.func.max(UserAnswer.answered_at)).filter_by(attempt_id=a.id).scalar()
        finished = min(last or a.started_at, deadline)
        a.is_completed = True
        a.completed_at = finished
        a.time_spent_seconds = max(0, int((finished - a.started_at).total_seconds()))
        db.session.commit()
        a.calculate_score()
        print(f'✅ Đã chốt #{a.id} {a.user_name}: {a.correct_answers} đúng / {a.wrong_answers} sai, điểm {a.score}%')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        main(apply='--apply' in sys.argv)
