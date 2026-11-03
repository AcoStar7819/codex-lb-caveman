"""Add default-off per-key Caveman context projection."""

import sqlalchemy as sa
from alembic import op

revision = "20261103_000000_add_api_key_caveman"
down_revision = "20260918_000000_merge_scim_and_overflow_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("api_keys", sa.Column("caveman_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table("api_keys") as batch_op:
        batch_op.drop_column("caveman_enabled")
