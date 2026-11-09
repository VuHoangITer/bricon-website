"""quiz: them cau hoi tu luan (essay)

- questions.model_answer: dap an tham khao cho HR (khong hien thi cho nguoi lam bai)
- user_answers.text_answer: bai lam tu luan
- user_answers.answer_id: cho phep NULL (cau tu luan khong co dap an chon)

Revision ID: a7c3e91d2b40
Revises: c0dfb662488d
Create Date: 2026-11-09 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c3e91d2b40'
down_revision = 'c0dfb662488d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model_answer', sa.Text(), nullable=True))

    with op.batch_alter_table('user_answers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text_answer', sa.Text(), nullable=True))
        batch_op.alter_column('answer_id', existing_type=sa.Integer(), nullable=True)


def downgrade():
    # Xoa bai lam tu luan truoc khi dat lai NOT NULL cho answer_id
    op.execute('DELETE FROM user_answers WHERE answer_id IS NULL')

    with op.batch_alter_table('user_answers', schema=None) as batch_op:
        batch_op.alter_column('answer_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('text_answer')

    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_column('model_answer')
