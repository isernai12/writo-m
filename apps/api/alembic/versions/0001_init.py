"""init

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("maintenance_mode", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text()),
        sa.Column("avatar_url", sa.String(length=500)),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("is_banned", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("excerpt", sa.Text()),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500)),
        sa.Column("trending_thumbnail_url", sa.String(length=500)),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("read_time_minutes", sa.Integer(), nullable=False),
        sa.Column("love_count", sa.Integer(), nullable=False),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id")),
    )
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "post_id", name="uniq_bookmark"),
    )
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "post_id", name="uniq_reaction"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("details", sa.Text()),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id")),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id")),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("reactions")
    op.drop_table("bookmarks")
    op.drop_table("comments")
    op.drop_table("posts")
    op.drop_table("categories")
    op.drop_table("users")
    op.drop_table("site_settings")
