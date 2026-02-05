"""change_vector_dimension_to_1024

Revision ID: 0103d2463bba
Revises: 086bfce243f6
Create Date: 2026-02-04

Changes vector columns from 1536 (OpenAI) to 1024 (Voyage) dimensions.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0103d2463bba"
down_revision: str | Sequence[str] | None = "086bfce243f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change vector dimension from 1536 to 1024 for Voyage embeddings."""

    # Drop existing vector indexes
    op.execute("DROP INDEX IF EXISTS idx_memories_embedding")
    op.execute("DROP INDEX IF EXISTS idx_conversations_embedding")

    # Drop existing vector columns
    op.execute("ALTER TABLE memories DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS embedding")

    # Add new vector columns with 1024 dimensions (Voyage voyage-3)
    op.execute("ALTER TABLE memories ADD COLUMN embedding vector(1024)")
    op.execute("ALTER TABLE conversations ADD COLUMN embedding vector(1024)")

    # Recreate IVFFlat indexes for approximate nearest neighbor search
    op.execute(
        "CREATE INDEX idx_memories_embedding ON memories "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.execute(
        "CREATE INDEX idx_conversations_embedding ON conversations "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    """Revert vector dimension back to 1536 for OpenAI embeddings."""

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_memories_embedding")
    op.execute("DROP INDEX IF EXISTS idx_conversations_embedding")

    # Drop 1024 columns
    op.execute("ALTER TABLE memories DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS embedding")

    # Restore 1536 columns (OpenAI)
    op.execute("ALTER TABLE memories ADD COLUMN embedding vector(1536)")
    op.execute("ALTER TABLE conversations ADD COLUMN embedding vector(1536)")

    # Recreate indexes
    op.execute(
        "CREATE INDEX idx_memories_embedding ON memories "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.execute(
        "CREATE INDEX idx_conversations_embedding ON conversations "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
