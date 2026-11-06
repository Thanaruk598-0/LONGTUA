from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.auth import AuthSchema


class ActivityCreate(AuthSchema):
    activity_type: str = "TASK"
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    date_start: date
    date_end: date | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    deadline_at: datetime | None = None
    notification_override: dict | None = None


class ActivityUpdate(AuthSchema):
    activity_type: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    date_start: date | None = None
    date_end: date | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    deadline_at: datetime | None = None
    notification_override: dict | None = None


class ActivityResponse(AuthSchema):
    id: UUID
    object_type: str
    activity_type: str | None
    title: str
    description: str | None
    status: str
    date_start: date
    date_end: date | None
    start_at: datetime | None
    end_at: datetime | None
    duration_minutes: int | None
    deadline_at: datetime | None

    model_config = {"from_attributes": True}


class PlanningRequestCreate(AuthSchema):
    input_text: str = Field(min_length=1, max_length=1000)
    reference_time: datetime | None = None


class ProposalAction(AuthSchema):
    reason: str | None = None


class ProposalItemResponse(AuthSchema):
    planning_object_id: UUID
    plan_key: str
    start_at: datetime
    end_at: datetime

    model_config = {"from_attributes": True}
