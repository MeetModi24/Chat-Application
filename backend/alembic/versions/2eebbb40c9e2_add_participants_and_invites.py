"""add participants and invites

Revision ID: 2eebbb40c9e2
Revises: 0001_initial
Create Date: 2025-08-15 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic
revision = "2eebbb40c9e2"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # ---------- participants ----------
    op.create_table(
        "chat_session_participants",
        sa.Column("session_id", pg.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ---------- invites ----------
    op.create_table(
        "chat_invites",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", pg.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_by_user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("session_id", "email", name="uq_chat_invites_session_email"),
    )
    op.create_index("ix_chat_invites_email", "chat_invites", ["email"])
    op.create_index("ix_chat_invites_token", "chat_invites", ["token"])


def downgrade():
    op.drop_index("ix_chat_invites_token", table_name="chat_invites")
    op.drop_index("ix_chat_invites_email", table_name="chat_invites")
    op.drop_table("chat_invites")
    op.drop_table("chat_session_participants")
