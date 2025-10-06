"""add role to user"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251006141130"
down_revision = None  # <-- set to your current head manually if needed
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(length=20), nullable=False, server_default="user"))
    # remove default after applying for existing rows
    op.execute("UPDATE user SET role = 'user' WHERE role IS NULL")
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("role", server_default=None)

def downgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("role")
