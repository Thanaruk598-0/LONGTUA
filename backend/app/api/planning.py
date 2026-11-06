from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.planning_object import PlanningObject
from app.models.planning_request import PlanningRequest
from app.models.proposal import Proposal
from app.models.proposal_item import ProposalItem
from app.models.schedule_item import ScheduleItem
from app.models.schedule_version import ScheduleVersion
from app.models.user import User
from app.schemas.planning import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    PlanningRequestCreate,
    ProposalAction,
)

router = APIRouter(tags=["Planning"])


def _activity_mode(payload: ActivityCreate | ActivityUpdate) -> str:
    if payload.start_at and payload.end_at:
        return "FIXED"
    if payload.duration_minutes:
        return "DURATION"
    return "DATE_ONLY"


def _get_activity(db: Session, user_id: UUID, activity_id: UUID) -> PlanningObject:
    activity = db.scalar(
        select(PlanningObject).where(
            PlanningObject.id == activity_id,
            PlanningObject.user_id == user_id,
            PlanningObject.deleted_at.is_(None),
        )
    )
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.get("/api/activities", response_model=list[ActivityResponse])
def list_activities(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[PlanningObject]:
    return list(
        db.scalars(
            select(PlanningObject)
            .where(PlanningObject.user_id == current_user.id, PlanningObject.deleted_at.is_(None))
            .order_by(PlanningObject.date_start, PlanningObject.created_at)
        )
    )


@router.post("/api/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanningObject:
    if (payload.start_at is None) != (payload.end_at is None):
        raise HTTPException(status_code=422, detail="startAt and endAt must be provided together")
    if payload.start_at and payload.end_at and payload.end_at <= payload.start_at:
        raise HTTPException(status_code=422, detail="endAt must be after startAt")
    activity = PlanningObject(
        user_id=current_user.id,
        object_type="ACTIVITY",
        activity_type=payload.activity_type,
        title=payload.title,
        description=payload.description,
        status="ACTIVE",
        date_start=payload.date_start,
        date_end=payload.date_end,
        time_mode=_activity_mode(payload),
        start_at=payload.start_at,
        end_at=payload.end_at,
        duration_minutes=payload.duration_minutes,
        deadline_at=payload.deadline_at,
        notification_override=payload.notification_override,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/api/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanningObject:
    return _get_activity(db, current_user.id, activity_id)


@router.patch("/api/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: UUID,
    payload: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanningObject:
    activity = _get_activity(db, current_user.id, activity_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    if activity.start_at and activity.end_at and activity.end_at <= activity.start_at:
        raise HTTPException(status_code=422, detail="endAt must be after startAt")
    activity.time_mode = "FIXED" if activity.start_at and activity.end_at else (
        "DURATION" if activity.duration_minutes else "DATE_ONLY"
    )
    db.commit()
    db.refresh(activity)
    return activity


@router.post("/api/activities/{activity_id}/cancel", response_model=ActivityResponse)
def cancel_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanningObject:
    activity = _get_activity(db, current_user.id, activity_id)
    activity.status = "CANCELLED"
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/api/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    activity = _get_activity(db, current_user.id, activity_id)
    activity.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _current_schedule(db: Session, user_id: UUID) -> ScheduleVersion | None:
    return db.scalar(
        select(ScheduleVersion).where(
            ScheduleVersion.user_id == user_id, ScheduleVersion.is_current.is_(True)
        )
    )


@router.get("/api/schedule")
def get_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    version = _current_schedule(db, current_user.id)
    if version is None:
        return {"scheduleVersion": None, "items": [], "unscheduled": []}
    items = list(db.scalars(select(ScheduleItem).where(ScheduleItem.schedule_version_id == version.id)))
    scheduled_ids = {item.planning_object_id for item in items}
    activities = list(
        db.scalars(
            select(PlanningObject).where(
                PlanningObject.user_id == current_user.id,
                PlanningObject.deleted_at.is_(None),
            )
        )
    )
    return {
        "scheduleVersion": {
            "id": str(version.id),
            "versionNumber": version.version_number,
            "isCurrent": version.is_current,
        },
        "items": [
            {
                "id": str(item.id),
                "planningObjectId": str(item.planning_object_id),
                "startAt": item.start_at,
                "endAt": item.end_at,
            }
            for item in items
        ],
        "unscheduled": [
            {"planningObjectId": str(a.id), "date": a.date_start, "title": a.title}
            for a in activities
            if a.id not in scheduled_ids
        ],
    }


@router.post("/api/planning/requests", status_code=status.HTTP_201_CREATED)
def create_planning_request(
    payload: PlanningRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    reference = payload.reference_time or datetime.now(timezone.utc)
    request = PlanningRequest(
        user_id=current_user.id,
        request_type="PLANNING",
        status="COMPLETED",
        input_text=payload.input_text,
        reference_time=reference,
    )
    db.add(request)
    db.flush()
    source_version = _current_schedule(db, current_user.id)
    proposal = Proposal(
        user_id=current_user.id,
        planning_request_id=request.id,
        source_schedule_version_id=source_version.id if source_version else None,
        status="PENDING",
        candidate_count=1,
        metadata_json={"mode": "RULE_BASED_PLANNER"},
    )
    db.add(proposal)
    db.flush()
    activities = list(
        db.scalars(
            select(PlanningObject)
            .where(
                PlanningObject.user_id == current_user.id,
                PlanningObject.status == "ACTIVE",
                PlanningObject.deleted_at.is_(None),
            )
            .order_by(PlanningObject.date_start, PlanningObject.created_at)
        )
    )
    fallback = datetime.combine(reference.date(), time(9), tzinfo=reference.tzinfo)
    for activity in activities:
        start = activity.start_at or fallback
        end = activity.end_at or start + timedelta(minutes=activity.duration_minutes or 60)
        db.add(
            ProposalItem(
                proposal_id=proposal.id,
                plan_key="A",
                planning_object_id=activity.id,
                start_at=start,
                end_at=end,
                metadata_json={"source": "RULE_BASED_PLANNER"},
            )
        )
        fallback = end + timedelta(minutes=30)
    db.commit()
    return {
        "requestId": str(request.id),
        "proposalId": str(proposal.id),
        "status": proposal.status,
        "candidateItems": [
            {
                "planningObjectId": str(item.planning_object_id),
                "title": next(
                    activity.title for activity in activities if activity.id == item.planning_object_id
                ),
                "startAt": item.start_at,
                "endAt": item.end_at,
            }
            for item in db.scalars(
                select(ProposalItem).where(
                    ProposalItem.proposal_id == proposal.id,
                    ProposalItem.plan_key == "A",
                )
            )
        ],
    }


@router.post("/api/proposals/{proposal_id}/reject")
def reject_proposal(
    proposal_id: UUID,
    payload: ProposalAction | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    proposal = db.scalar(select(Proposal).where(Proposal.id == proposal_id, Proposal.user_id == current_user.id))
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "PENDING":
        raise HTTPException(status_code=409, detail="Proposal is not pending")
    proposal.status = "REJECTED"
    proposal.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": str(proposal.id), "status": proposal.status}


@router.post("/api/proposals/{proposal_id}/confirm")
def confirm_proposal(
    proposal_id: UUID,
    payload: ProposalAction | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    proposal = db.scalar(select(Proposal).where(Proposal.id == proposal_id, Proposal.user_id == current_user.id))
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "PENDING":
        raise HTTPException(status_code=409, detail="Proposal is not pending")
    current = _current_schedule(db, current_user.id)
    if (current and proposal.source_schedule_version_id != current.id) or (
        not current and proposal.source_schedule_version_id is not None
    ):
        raise HTTPException(status_code=409, detail="Proposal is based on a stale schedule")
    previous = db.scalars(select(ScheduleVersion).where(ScheduleVersion.user_id == current_user.id)).all()
    for version in previous:
        version.is_current = False
    version = ScheduleVersion(
        user_id=current_user.id,
        version_number=max((v.version_number for v in previous), default=0) + 1,
        is_current=True,
        confirmation_source="PROPOSAL",
        source_request_id=proposal.planning_request_id,
    )
    db.add(version)
    db.flush()
    items = list(db.scalars(select(ProposalItem).where(ProposalItem.proposal_id == proposal.id, ProposalItem.plan_key == "A")))
    for item in items:
        db.add(
            ScheduleItem(
                schedule_version_id=version.id,
                planning_object_id=item.planning_object_id,
                start_at=item.start_at,
                end_at=item.end_at,
                metadata_json=item.metadata_json,
            )
        )
    proposal.status = "CONFIRMED"
    proposal.selected_plan_key = "A"
    proposal.confirmed_at = datetime.now(timezone.utc)
    proposal.reviewed_at = proposal.confirmed_at
    db.commit()
    return {"id": str(proposal.id), "status": proposal.status, "scheduleVersionId": str(version.id)}
