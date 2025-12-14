"""add scheduled publishing to blog

Revision ID: 7ecf9bf18aa3
Revises: e6cbe5f5824c
Create Date: 2025-12-13 21:59:16.457000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '7ecf9bf18aa3'
down_revision = 'e6cbe5f5824c'
branch_labels = None
depends_on = None


def upgrade():
    # ==================== BƯỚC 1: ADD COLUMNS (NULLABLE) ====================
    # Thêm columns với nullable=True trước
    with op.batch_alter_table('blogs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('scheduled_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('published_at', sa.DateTime(), nullable=True))

    # ==================== BƯỚC 2: MIGRATE DỮ LIỆU CŨ ====================
    # Set status = 'published' cho bài is_active = True
    op.execute("""
        UPDATE blogs 
        SET status = 'published', 
            published_at = created_at 
        WHERE is_active = TRUE AND status IS NULL
    """)

    # Set status = 'draft' cho bài is_active = False
    op.execute("""
        UPDATE blogs 
        SET status = 'draft' 
        WHERE is_active = FALSE AND status IS NULL
    """)

    # Set default 'draft' cho những bài còn NULL (nếu có)
    op.execute("""
        UPDATE blogs 
        SET status = 'draft' 
        WHERE status IS NULL
    """)

    # ==================== BƯỚC 3: ALTER COLUMN → NOT NULL ====================
    with op.batch_alter_table('blogs', schema=None) as batch_op:
        batch_op.alter_column('status',
                              existing_type=sa.String(length=20),
                              nullable=False,
                              server_default='draft'
                              )

    # ==================== BƯỚC 4: CREATE INDEXES ====================
    with op.batch_alter_table('blogs', schema=None) as batch_op:
        batch_op.create_index('ix_blogs_status', ['status'], unique=False)
        batch_op.create_index('ix_blogs_scheduled_at', ['scheduled_at'], unique=False)


def downgrade():
    # ==================== ROLLBACK ====================
    with op.batch_alter_table('blogs', schema=None) as batch_op:
        batch_op.drop_index('ix_blogs_scheduled_at')
        batch_op.drop_index('ix_blogs_status')
        batch_op.drop_column('published_at')
        batch_op.drop_column('scheduled_at')
        batch_op.drop_column('status')