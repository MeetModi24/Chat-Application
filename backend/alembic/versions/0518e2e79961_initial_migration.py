"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2025-08-16 07:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import enum

# revision identifiers, used by Alembic.
revision = '0518e2e79961'
down_revision = None
branch_labels = None
depends_on = None

# ---------------------- ENUMS ----------------------
class MessageRoleEnum(str, enum.Enum):
    user = "user"
    agent = "agent"
    system = "system"
    tool = "tool"

def upgrade():
    # ---------------------- USERS ----------------------
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # ---------------------- CHAT SESSIONS ----------------------
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, server_default="Untitled Session"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index('ix_chat_sessions_user_created', 'chat_sessions', ['user_id', 'created_at'])

    # ---------------------- CHAT SESSION PARTICIPANTS ----------------------
    op.create_table(
        'chat_session_participants',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role', sa.String, nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # ---------------------- CHAT INVITES ----------------------
    op.create_table(
        'chat_invites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('token', sa.String, nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked', sa.Boolean, server_default=sa.false())
    )
    op.create_unique_constraint('uq_chat_invites_session_email', 'chat_invites', ['session_id', 'email'])
    op.create_index('ix_chat_invites_session_id', 'chat_invites', ['session_id'])
    op.create_index('ix_chat_invites_email', 'chat_invites', ['email'])
    op.create_index('ix_chat_invites_token', 'chat_invites', ['token'])

    # ---------------------- MESSAGES ----------------------
    message_role_enum = sa.Enum(MessageRoleEnum, name='message_role_enum')

    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tool_calls', postgresql.JSONB, nullable=True),
        sa.Column('tool_metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create the enum type only if it doesn't exist yet
    message_role_enum.create(op.get_bind(), checkfirst=True)
    op.create_index('ix_messages_session_created', 'messages', ['session_id', 'created_at'])



def downgrade():
    op.drop_index('ix_messages_session_created', table_name='messages')
    op.drop_table('messages')
    op.execute('DROP TYPE IF EXISTS message_role_enum')

    op.drop_index('ix_chat_invites_token', table_name='chat_invites')
    op.drop_index('ix_chat_invites_email', table_name='chat_invites')
    op.drop_index('ix_chat_invites_session_id', table_name='chat_invites')
    op.drop_table('chat_invites')

    op.drop_table('chat_session_participants')
    op.drop_index('ix_chat_sessions_user_created', table_name='chat_sessions')
    op.drop_table('chat_sessions')

    op.drop_table('users')
