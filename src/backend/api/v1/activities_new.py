"""
New Activities API (vote/thread) per activity-system-design.md

Endpoints (all under /api/v1/activities):
 - GET    /api/v1/activities
 - GET    /api/v1/activities/{activity_id}
 - GET    /api/v1/activities/{activity_id}/ranking
 - GET    /api/v1/activities/{activity_id}/options
 - POST   /api/v1/activities/{activity_id}/vote
 - DELETE /api/v1/activities/{activity_id}/vote
 - GET    /api/v1/activities/{activity_id}/posts
 - POST   /api/v1/activities/{activity_id}/posts
 - POST   /api/v1/activities/{activity_id}/close (admin)
 - POST   /api/v1/activities/seed-demo (admin) - helper for demo data
 - POST   /api/v1/activities                (create activity)
 - POST   /api/v1/activities/{activity_id}/options (create vote option)
"""
from __future__ import annotations

from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session, get_cache_service, get_config_service
from services.auth.utils import get_current_active_user, get_current_user_optional, require_admin
from services.database.models.user import User
from services.database.models.activity_subsystem.base import (
    ActActivity,
    ActVoteOption,
    ActAuditLog,
)
from services.database.models.activity_subsystem.crud import (
    ActActivityCRUD,
    ActVoteCRUD,
    ActThreadCRUD,
)
from services.database.models.base import orjson_dumps_compact, to_naive_beijing
from schema.activity2 import (
    ActivityCreate,
    ActivityOut,
    VoteSubmit,
    ThreadPostCreate,
    VoteOptionCreate,
    VoteOptionOut,
    RankingOut,
    ActivityListOut,
    ActivityListItem,
)


router = APIRouter(prefix="/activities", tags=["activities-new"])


def _parse_optional_naive(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        return to_naive_beijing(dt)
    except Exception:
        # 宽松处理：若解析失败，返回None
        return None


@router.get("", response_model=ActivityListOut)
async def list_activities(
    status: str = Query("ongoing"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    cache = get_cache_service()
    settings = get_config_service().get_settings()
    ttl = min(getattr(settings, "cache_activity_ttl", 300), 10)
    cache_key = f"act:list:{status}:{page}:{size}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    items, total = await ActActivityCRUD.list(session, status=status, page=page, size=size)
    payload: ActivityListOut = ActivityListOut(
        items=[
            ActivityListItem(
                id=a.id,
                type=a.type,
                title=a.title,
                description=a.description,
                status=a.status,
                creator_id=getattr(a, "creator_id", 0),
            )
            for a in items
        ],
        total=total,
        page=page,
        size=size,
    )
    await cache.set(cache_key, payload.model_dump(mode="json"), ttl=ttl)
    return payload


@router.get("/{activity_id}", response_model=ActivityOut)
async def get_activity(activity_id: int, session: AsyncSession = Depends(get_session)):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityOut(
        id=a.id,
        type=a.type,
        title=a.title,
        description=a.description,
        status=a.status,
        anonymous_allowed=a.anonymous_allowed,
        allow_change=a.allow_change,
        starts_at=a.starts_at.isoformat() if a.starts_at else None,
        ends_at=a.ends_at.isoformat() if a.ends_at else None,
        creator_id=getattr(a, "creator_id", 0),
    )


@router.get("/{activity_id}/ranking", response_model=RankingOut)
async def get_ranking(
    activity_id: int,
    top: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")

    cache = get_cache_service()
    settings = get_config_service().get_settings()
    ttl = min(getattr(settings, "cache_activity_ttl", 300), 10)
    cache_key = f"act:rank:{activity_id}:{top}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    rows = await ActVoteCRUD.get_ranking(session, activity_id, top=top)
    opts = await ActVoteCRUD.list_options(session, activity_id, None, 1000)
    id2label = {o.id: o.label for o in opts}
    payload = {
        "entries": [
            {"option_id": oid, "label": id2label.get(oid, str(oid)), "votes": cnt}
            for oid, cnt in rows
        ]
    }
    await cache.set(cache_key, payload, ttl=ttl)
    return payload


@router.get("/{activity_id}/my-vote")
async def get_my_vote(
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "vote":
        raise HTTPException(status_code=404, detail="Vote activity not found")
    record = await ActVoteCRUD.get_vote_record(session, activity_id, current_user.id)
    if not record:
        return {"option_id": None}
    return {"option_id": record.option_id}

@router.get("/{activity_id}/options", response_model=dict)
async def list_options(
    activity_id: int,
    query: Optional[str] = None,
    size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    items = await ActVoteCRUD.list_options(session, activity_id, query=query, size=size)
    return {"items": [{"id": o.id, "label": o.label, "member_id": o.member_id} for o in items]}


@router.post("/{activity_id}/options", response_model=VoteOptionOut)
async def create_option(
    activity_id: int,
    option: VoteOptionCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "vote":
        raise HTTPException(status_code=404, detail="Vote activity not found")

    # 权限：管理员或活动发起者可新增选项
    if not (getattr(current_user, "role", None) == "admin" or getattr(a, "creator_id", 0) == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to add options")

    # create option
    created = ActVoteOption(activity_id=activity_id, label=option.label, member_id=option.member_id)
    session.add(created)
    await session.commit()
    await session.refresh(created)

    # audit
    meta = {"activity_id": activity_id, "option_id": created.id, "label": option.label, "member_id": option.member_id}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=current_user.id, action="create_option", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return VoteOptionOut(id=created.id, label=created.label, member_id=created.member_id)


@router.delete("/{activity_id}/options/{option_id}")
async def delete_option(
    activity_id: int,
    option_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "vote":
        raise HTTPException(status_code=404, detail="Vote activity not found")
    if not (getattr(current_user, "role", None) == "admin" or getattr(a, "creator_id", 0) == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to delete options")

    opt = await session.get(ActVoteOption, option_id)
    if not opt or opt.activity_id != activity_id:
        raise HTTPException(status_code=404, detail="Option not found")
    await session.delete(opt)
    await session.commit()

    # audit
    meta = {"activity_id": activity_id, "option_id": option_id}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=current_user.id, action="delete_option", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return {"success": True}


@router.post("", response_model=ActivityOut)
async def create_activity(
    payload: ActivityCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    starts_at = _parse_optional_naive(payload.starts_at)
    ends_at = _parse_optional_naive(payload.ends_at)

    a = ActActivity(
        type=payload.type,
        title=payload.title,
        description=payload.description,
        anonymous_allowed=payload.anonymous_allowed,
        allow_change=payload.allow_change,
        starts_at=starts_at,
        ends_at=ends_at,
        status="ongoing",
        creator_id=current_user.id,
    )
    session.add(a)
    await session.commit()
    await session.refresh(a)

    # audit
    meta = {"creator_id": current_user.id, "activity_id": a.id, "title": a.title, "type": a.type}
    session.add(ActAuditLog(activity_id=a.id, actor_id=current_user.id, action="create_activity", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return ActivityOut(
        id=a.id,
        type=a.type,
        title=a.title,
        description=a.description,
        status=a.status,
        anonymous_allowed=a.anonymous_allowed,
        allow_change=a.allow_change,
        starts_at=a.starts_at.isoformat() if a.starts_at else None,
        ends_at=a.ends_at.isoformat() if a.ends_at else None,
        creator_id=getattr(a, "creator_id", 0),
    )


@router.post("/{activity_id}/vote")
async def submit_vote(
    activity_id: int,
    vote: VoteSubmit,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "vote":
        raise HTTPException(status_code=404, detail="Vote activity not found")
    if a.status != "ongoing":
        raise HTTPException(status_code=400, detail="Activity not ongoing")

    # ensure option exists under this activity
    opts = await ActVoteCRUD.list_options(session, activity_id, None, 1_000)
    if vote.option_id not in {o.id for o in opts}:
        raise HTTPException(status_code=400, detail="Invalid option")

    await ActVoteCRUD.upsert_vote(
        session,
        activity_id=activity_id,
        option_id=vote.option_id,
        voter_id=current_user.id,
        display_anonymous=vote.display_anonymous,
    )

    # audit
    meta = {"activity_id": activity_id, "option_id": vote.option_id, "voter_id": current_user.id, "anonymous": vote.display_anonymous}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=current_user.id, action="submit_vote", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return {"success": True}


@router.delete("/{activity_id}/vote")
async def revoke_vote(
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "vote":
        raise HTTPException(status_code=404, detail="Vote activity not found")
    ok = await ActVoteCRUD.revoke_vote(session, activity_id, current_user.id)

    # audit
    meta = {"activity_id": activity_id, "voter_id": current_user.id, "revoked": ok}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=current_user.id, action="revoke_vote", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return {"success": ok}


@router.get("/{activity_id}/posts")
async def list_posts(activity_id: int, size: int = 20, session: AsyncSession = Depends(get_session)):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "thread":
        raise HTTPException(status_code=404, detail="Thread activity not found")
    items = await ActThreadCRUD.list_posts(session, activity_id, size=size)
    return {"items": [
        {
            "id": p.id,
            "activity_id": p.activity_id,
            "author_id": p.author_id,
            "display_anonymous": p.display_anonymous,
            "content": p.content,
            "parent_id": p.parent_id,
            "created_at": p.created_at,
        }
        for p in items
    ]}


@router.post("/{activity_id}/posts")
async def create_post(
    activity_id: int,
    post: ThreadPostCreate,
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a or a.type != "thread":
        raise HTTPException(status_code=404, detail="Thread activity not found")

    content = post.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Empty content")

    # Rule: allow anonymous posting without login only when the activity allows it AND client sets display_anonymous=true
    # Otherwise, require authenticated user
    if current_user is None and not (a.anonymous_allowed and post.display_anonymous):
        raise HTTPException(status_code=401, detail="Not authenticated")

    author_id = current_user.id if current_user is not None else 0

    created = await ActThreadCRUD.create_post(
        session,
        activity_id=activity_id,
        author_id=author_id,
        content=content,
        display_anonymous=post.display_anonymous,
        parent_id=post.parent_id,
    )

    # audit
    meta = {"activity_id": activity_id, "post_id": created.id, "author_id": author_id, "anonymous": post.display_anonymous}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=author_id, action="create_post", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return {
        "id": created.id,
        "activity_id": created.activity_id,
        "author_id": created.author_id,
        "display_anonymous": created.display_anonymous,
        "content": created.content,
        "parent_id": created.parent_id,
        "created_at": created.created_at,
    }


@router.post("/{activity_id}/close")
async def close_activity(activity_id: int, _: dict = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    a.status = "closed"
    session.add(a)
    await session.commit()

    # audit
    meta = {"activity_id": activity_id}
    session.add(ActAuditLog(activity_id=activity_id, actor_id=0, action="close_activity", metadata_json=orjson_dumps_compact(meta)))
    await session.commit()

    return {"success": True}


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    a = await ActActivityCRUD.get(session, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")

    # 权限：管理员或活动创建者
    if not (getattr(current_user, "role", None) == "admin" or getattr(a, "creator_id", 0) == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to delete activity")

    ok = await ActActivityCRUD.delete(session, activity_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Activity not found")
    return {"success": True}


@router.post("/seed-demo")
async def seed_demo(_: dict = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    """Seed minimal demo data for UI testing."""
    # create a vote activity with 4 options if none exists
    from sqlmodel import select

    existing = (await session.exec(select(ActActivity).limit(1))).first()
    if existing:
        return {"message": "already seeded"}

    vote = ActActivity(type="vote", title="最受欢迎的成员", description="投票示例", status="ongoing")
    thread = ActActivity(type="thread", title="话题讨论区", description="讨论示例", status="ongoing")
    session.add(vote)
    session.add(thread)
    await session.commit()
    await session.refresh(vote)
    await session.refresh(thread)

    for label in ["Alice", "Bob", "Carol", "Dave"]:
        session.add(ActVoteOption(activity_id=vote.id, label=label))
    await session.commit()

    return {"success": True, "vote_activity_id": vote.id, "thread_activity_id": thread.id}


