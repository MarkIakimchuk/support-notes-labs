from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"


def upgrade():
    op.add_column("users", sa.Column("password_hash", sa.String(60), nullable=True))
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "access_token",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "refresh_id", sa.Uuid(), sa.ForeignKey("refresh_token.id", ondelete="CASCADE"),
            nullable=False, unique=True,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("access_token")
    op.drop_table("refresh_token")
    op.drop_column("users", "password_hash")
