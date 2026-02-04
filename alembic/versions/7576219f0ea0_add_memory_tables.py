"""add_memory_tables

Revision ID: 7576219f0ea0
Revises: 4e4966e1a4ee
Create Date: 2026-02-04 14:19:18.064602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = '7576219f0ea0'
down_revision: Union[str, Sequence[str], None] = '4e4966e1a4ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add memory, predictions, conversations, and related tables."""

    # Detected Patterns table (yogas and doshas)
    op.create_table(
        "detected_patterns",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("pattern_type", sa.String(20), nullable=False),  # 'yoga' or 'dosha'
        sa.Column("pattern_id", sa.String(50), nullable=False),
        sa.Column("pattern_name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("strength", sa.Numeric(3, 2), nullable=True),
        sa.Column("severity", sa.String(20), nullable=True),  # For doshas
        sa.Column("involved_planets", ARRAY(sa.Text), nullable=True),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("detected_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_detected_patterns_user", "detected_patterns", ["user_id"])
    op.create_index("idx_detected_patterns_type", "detected_patterns", ["user_id", "pattern_type"])

    # Memories table with vector embeddings
    op.create_table(
        "memories",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),  # fact, preference, event, prediction, feedback
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("importance", sa.Numeric(3, 2), server_default=sa.text("0.5"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    # Add vector column using raw SQL (pgvector)
    op.execute("ALTER TABLE memories ADD COLUMN embedding vector(1536)")
    op.create_index("idx_memories_user", "memories", ["user_id"])
    op.create_index("idx_memories_category", "memories", ["user_id", "category"])
    op.create_index("idx_memories_importance", "memories", ["user_id", "importance"])
    # Vector similarity index (IVFFlat for approximate nearest neighbor)
    op.execute(
        "CREATE INDEX idx_memories_embedding ON memories "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # Predictions table
    op.create_table(
        "predictions",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("prediction_text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("timeframe_start", sa.Date(), nullable=True),
        sa.Column("timeframe_end", sa.Date(), nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("factors", JSONB, nullable=True),
        sa.Column("dasha_period", JSONB, nullable=True),
        sa.Column("transit_positions", JSONB, nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("accuracy", sa.Numeric(3, 2), nullable=True),
        sa.Column("validated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_predictions_user", "predictions", ["user_id"])
    op.create_index("idx_predictions_category", "predictions", ["user_id", "category"])
    op.create_index("idx_predictions_timeframe", "predictions", ["user_id", "timeframe_start", "timeframe_end"])

    # Conversations table
    op.create_table(
        "conversations",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("messages", JSONB, nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("topics", ARRAY(sa.Text), nullable=True),
        sa.Column("message_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    # Add vector column for conversation embeddings
    op.execute("ALTER TABLE conversations ADD COLUMN embedding vector(1536)")
    op.create_index("idx_conversations_user", "conversations", ["user_id"])
    op.create_index("idx_conversations_session", "conversations", ["session_id"])
    op.execute(
        "CREATE INDEX idx_conversations_embedding ON conversations "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # User Preferences table
    op.create_table(
        "user_preferences",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("preference_key", sa.String(100), nullable=False),
        sa.Column("preference_value", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "preference_key", name="uq_user_preferences_key"),
    )
    op.create_index("idx_user_preferences_user", "user_preferences", ["user_id"])

    # Dasha Timeline table (cached dasha periods)
    op.create_table(
        "dasha_timeline",
        sa.Column("id", UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),  # maha, antar, pratyantar
        sa.Column("lord", sa.String(20), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("parent_id", UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["dasha_timeline.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_dasha_timeline_user", "dasha_timeline", ["user_id"])
    op.create_index("idx_dasha_timeline_dates", "dasha_timeline", ["user_id", "start_date", "end_date"])
    op.create_index("idx_dasha_timeline_lord", "dasha_timeline", ["user_id", "lord"])

    # Add updated_at triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE 'plpgsql';
    """)

    op.execute("CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories "
               "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations "
               "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences "
               "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")


def downgrade() -> None:
    """Remove memory tables."""
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences")
    op.execute("DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations")
    op.execute("DROP TRIGGER IF EXISTS update_memories_updated_at ON memories")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop indexes
    op.drop_index("idx_dasha_timeline_lord", table_name="dasha_timeline")
    op.drop_index("idx_dasha_timeline_dates", table_name="dasha_timeline")
    op.drop_index("idx_dasha_timeline_user", table_name="dasha_timeline")

    op.drop_index("idx_user_preferences_user", table_name="user_preferences")

    op.execute("DROP INDEX IF EXISTS idx_conversations_embedding")
    op.drop_index("idx_conversations_session", table_name="conversations")
    op.drop_index("idx_conversations_user", table_name="conversations")

    op.drop_index("idx_predictions_timeframe", table_name="predictions")
    op.drop_index("idx_predictions_category", table_name="predictions")
    op.drop_index("idx_predictions_user", table_name="predictions")

    op.execute("DROP INDEX IF EXISTS idx_memories_embedding")
    op.drop_index("idx_memories_importance", table_name="memories")
    op.drop_index("idx_memories_category", table_name="memories")
    op.drop_index("idx_memories_user", table_name="memories")

    op.drop_index("idx_detected_patterns_type", table_name="detected_patterns")
    op.drop_index("idx_detected_patterns_user", table_name="detected_patterns")

    # Drop tables
    op.drop_table("dasha_timeline")
    op.drop_table("user_preferences")
    op.drop_table("conversations")
    op.drop_table("predictions")
    op.drop_table("memories")
    op.drop_table("detected_patterns")
