"""add demo planning vertical slice

Revision ID: 9f7c3b1a2d44
Revises: 8d4f2a1b7c90
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "9f7c3b1a2d44"
down_revision: Union[str, Sequence[str], None] = "8d4f2a1b7c90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid_fk(table: str, column: str, target: str, ondelete: str = "CASCADE"):
    return sa.Column(
        column,
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(target, ondelete=ondelete),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "planning_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("planning_requests", "user_id", "users.id"),
        sa.Column("request_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("reference_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planning_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planning_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_planning_requests_user_id", "planning_requests", ["user_id"])

    op.create_table(
        "planning_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("planning_objects", "user_id", "users.id"),
        sa.Column("object_type", sa.String(20), nullable=False),
        sa.Column("activity_type", sa.String(32), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=True),
        sa.Column("time_mode", sa.String(24), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("semantic_window", sa.String(32), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("duration_qualifier", sa.String(20), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notification_override", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("planning_requests.id", ondelete="SET NULL"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_planning_objects_user_id", "planning_objects", ["user_id"])

    op.create_table(
        "schedule_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("schedule_versions", "user_id", "users.id"),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("confirmation_source", sa.String(20), nullable=False),
        sa.Column("source_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("planning_requests.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "version_number"),
    )
    op.create_index("ix_schedule_versions_user_id", "schedule_versions", ["user_id"])

    op.create_table(
        "proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("proposals", "user_id", "users.id"),
        _uuid_fk("proposals", "planning_request_id", "planning_requests.id"),
        sa.Column("source_schedule_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schedule_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("candidate_count", sa.Integer(), nullable=False),
        sa.Column("selected_plan_key", sa.String(1), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_proposals_user_id", "proposals", ["user_id"])

    op.create_table(
        "proposal_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("proposal_items", "proposal_id", "proposals.id"),
        sa.Column("plan_key", sa.String(1), nullable=False),
        _uuid_fk("proposal_items", "planning_object_id", "planning_objects.id"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("proposal_id", "plan_key", "planning_object_id"),
    )
    op.create_index("ix_proposal_items_proposal_id", "proposal_items", ["proposal_id"])

    op.create_table(
        "schedule_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("schedule_items", "schedule_version_id", "schedule_versions.id"),
        _uuid_fk("schedule_items", "planning_object_id", "planning_objects.id"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("schedule_version_id", "planning_object_id"),
    )
    op.create_index("ix_schedule_items_schedule_version_id", "schedule_items", ["schedule_version_id"])


def downgrade() -> None:
    op.drop_index("ix_schedule_items_schedule_version_id", table_name="schedule_items")
    op.drop_table("schedule_items")
    op.drop_index("ix_proposal_items_proposal_id", table_name="proposal_items")
    op.drop_table("proposal_items")
    op.drop_index("ix_proposals_user_id", table_name="proposals")
    op.drop_table("proposals")
    op.drop_index("ix_schedule_versions_user_id", table_name="schedule_versions")
    op.drop_table("schedule_versions")
    op.drop_index("ix_planning_objects_user_id", table_name="planning_objects")
    op.drop_table("planning_objects")
    op.drop_index("ix_planning_requests_user_id", table_name="planning_requests")
    op.drop_table("planning_requests")
