"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("clerk_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clerk_id"),
    )
    op.create_index("idx_users_clerk_id", "users", ["clerk_id"])

    op.create_table(
        "child_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("initial_interests", sa.Text(), nullable=False),
        sa.Column("avatar_config", postgresql.JSONB(), nullable=False),
        sa.Column("preference_summary", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_child_profiles_user_id", "child_profiles", ["user_id"])

    op.create_table(
        "stories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("child_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_content", sa.Text(), nullable=False),
        sa.Column("language_target", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("script_generated_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["child_profile_id"], ["child_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "language_target IN ('es', 'en', 'mixed_es_en')",
            name="stories_language_target_check",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'scripting', 'script_ready', 'approved', 'generating_images', 'completed', 'failed')",
            name="stories_status_check",
        ),
    )
    op.create_index("idx_stories_child_profile_id", "stories", ["child_profile_id"])
    op.create_index("idx_stories_status", "stories", ["status"])

    op.create_table(
        "story_panels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("story_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("panel_order", sa.Integer(), nullable=False),
        sa.Column("image_prompt", sa.Text(), nullable=False),
        sa.Column("scene_description", sa.Text(), nullable=False),
        sa.Column("narrative_text", sa.Text(), nullable=False),
        sa.Column("dialogue", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("generation_status", sa.String(40), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("story_id", "panel_order", name="story_panels_unique_order"),
        sa.CheckConstraint("panel_order BETWEEN 1 AND 5", name="story_panels_order_check"),
        sa.CheckConstraint(
            "generation_status IN ('pending', 'generated', 'failed')",
            name="story_panels_generation_status_check",
        ),
    )
    op.create_index("idx_story_panels_story_id", "story_panels", ["story_id"])

    op.create_table(
        "story_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("story_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("panel_order", sa.Integer(), nullable=False),
        sa.Column("reaction_type", sa.String(40), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_profile_id"], ["child_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("panel_order BETWEEN 1 AND 5", name="story_feedback_panel_order_check"),
        sa.CheckConstraint(
            "reaction_type IN ('love', 'funny', 'scary')",
            name="story_feedback_reaction_type_check",
        ),
    )
    op.create_index("idx_story_feedback_profile_id", "story_feedback", ["child_profile_id"])


def downgrade() -> None:
    op.drop_table("story_feedback")
    op.drop_table("story_panels")
    op.drop_table("stories")
    op.drop_table("child_profiles")
    op.drop_table("users")
