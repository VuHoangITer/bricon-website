"""quiz: moi cau hoi chi 1 cau tra loi trong 1 luot lam bai

- Xoa ban ghi user_answers bi trung (attempt_id, question_id), giu ban ghi moi nhat (id lon nhat)
- Tinh lai diem / so cau dung / sai / dat cho moi luot lam bai da nop
  (cau sai = chon sai + bo trong, giong QuizAttempt.calculate_score moi)
- Them rang buoc UNIQUE (attempt_id, question_id)

Revision ID: d4e8b2a61f73
Revises: a7c3e91d2b40
Create Date: 2026-11-16 15:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e8b2a61f73'
down_revision = 'a7c3e91d2b40'
branch_labels = None
depends_on = None


def _recalculate_attempt(conn, attempt_id):
    """Tinh lai diem giong QuizAttempt.calculate_score (bo qua cau tu luan)."""
    row = conn.execute(sa.text(
        'SELECT a.quiz_id, a.is_completed, q.pass_score '
        'FROM quiz_attempts a JOIN quizzes q ON q.id = a.quiz_id WHERE a.id = :id'
    ), {'id': attempt_id}).first()
    if row is None or not row.is_completed:
        return

    totals = conn.execute(sa.text(
        "SELECT COALESCE(SUM(points), 0) AS pts, COUNT(*) AS cnt FROM questions "
        "WHERE quiz_id = :qid AND COALESCE(question_type, 'multiple_choice') <> 'essay'"
    ), {'qid': row.quiz_id}).first()
    total_points, scored_count = totals.pts or 0, totals.cnt or 0

    answers = conn.execute(sa.text(
        "SELECT ua.is_correct, q.points FROM user_answers ua "
        "JOIN questions q ON q.id = ua.question_id "
        "WHERE ua.attempt_id = :id AND COALESCE(q.question_type, 'multiple_choice') <> 'essay'"
    ), {'id': attempt_id}).fetchall()

    correct = sum(1 for a in answers if a.is_correct)
    wrong = max(scored_count - correct, 0)
    earned = sum(a.points or 0 for a in answers if a.is_correct)
    score = round(earned / total_points * 100, 2) if total_points else 0
    passed = score >= (row.pass_score or 0)

    conn.execute(sa.text(
        'UPDATE quiz_attempts SET score = :score, correct_answers = :c, wrong_answers = :w, passed = :p '
        'WHERE id = :id'
    ), {'score': score, 'c': correct, 'w': wrong, 'p': passed, 'id': attempt_id})


def upgrade():
    conn = op.get_bind()

    # Xoa ban ghi trung, giu ban ghi co id lon nhat (lan chon sau cung)
    conn.execute(sa.text(
        'DELETE FROM user_answers WHERE id NOT IN ('
        '  SELECT max_id FROM (SELECT MAX(id) AS max_id FROM user_answers GROUP BY attempt_id, question_id) AS keep'
        ')'
    ))

    # Tinh lai moi luot da nop (sua ca loi trung ban ghi lan loi khong tinh cau bo trong)
    for r in conn.execute(sa.text('SELECT id FROM quiz_attempts WHERE is_completed = :t'), {'t': True}).fetchall():
        _recalculate_attempt(conn, r.id)

    with op.batch_alter_table('user_answers', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_user_answers_attempt_question', ['attempt_id', 'question_id'])


def downgrade():
    with op.batch_alter_table('user_answers', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_answers_attempt_question', type_='unique')
