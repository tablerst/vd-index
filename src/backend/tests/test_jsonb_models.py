import os
import pytest
from typing import AsyncIterator, List

from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession

# Imports from project
from services.database.service import DatabaseService
from services.database.models.activity.base import ActivityCreate
from services.database.models.activity.crud import ActivityCRUD
from services.database.models.daily_post.base import DailyPostCreate
from services.database.models.daily_post.crud import DailyPostCRUD
from services.database.models.user.base import User

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set; skipping DB-dependent JSONB tests")
    # Ensure asyncpg dialect for DatabaseService
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://")
    return url


@pytest.fixture(scope="session")
async def db(db_url: str) -> AsyncIterator[DatabaseService]:
    svc = DatabaseService(db_url)
    # 不在测试中运行迁移，要求外部已执行 alembic upgrade head
    try:
        yield svc
    finally:
        await svc.teardown()


@pytest.fixture
async def session(db: DatabaseService) -> AsyncIterator[AsyncSession]:
    async with db.with_session() as s:
        yield s


async def _ensure_user(session: AsyncSession) -> int:
    """Create a temporary user for FK if none exists; return user id.
    中文注释：DailyPost 需要 author_user_id 外键，这里测试时创建一个最小用户。
    """
    # naive check for existing user
    from sqlmodel import select
    from services.database.models.user.base import User

    result = await session.exec(select(User).limit(1))
    user = result.first()
    if user:
        return user.id  # type: ignore

    u = User(
        username="test_jsonb_user",
        password_hash="bcrypt$dummy",
        is_active=True,
        role="admin",
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u.id  # type: ignore


async def _cleanup_activity(session: AsyncSession, activity_id: int) -> None:
    from services.database.models.activity.base import Activity
    obj = await session.get(Activity, activity_id)
    if obj:
        await session.delete(obj)
        await session.commit()


async def _cleanup_daily_post(session: AsyncSession, post_id: int) -> None:
    from services.database.models.daily_post.base import DailyPost
    obj = await session.get(DailyPost, post_id)
    if obj:
        await session.delete(obj)
        await session.commit()


async def _cleanup_user(session: AsyncSession, user_id: int) -> None:
    obj = await session.get(User, user_id)
    if obj:
        await session.delete(obj)
        await session.commit()


async def test_activity_jsonb_roundtrip_and_queries(session: AsyncSession):
    # 中文注释：验证Activity.tags/participant_ids 使用 JSONB 后的读写与查询
    tags = ["中文标签", "测试", "tag3"]
    participants = [101, 202]

    # Create
    act = await ActivityCRUD.create(
        session,
        ActivityCreate(title="JSONB 活动", description="带中文标签", date=datetime.utcnow(), tags=tags, participant_ids=participants),
    )

    try:
        # Read back
        got = await session.get(type(act), act.id)  # type: ignore
        assert isinstance(got.tags, list)
        assert got.tags == tags
        assert isinstance(got.participant_ids, list)
        assert got.participant_ids == participants

        # Query by tag using contains
        res_by_tag = await ActivityCRUD.get_by_tag(session, "中文标签")
        assert any(a.id == act.id for a in res_by_tag)

        # Query by participant using JSONB @> operator in CRUD
        res_by_part = await ActivityCRUD.get_by_participant(session, participants[0])
        assert any(a.id == act.id for a in res_by_part)
    finally:
        await _cleanup_activity(session, act.id)  # type: ignore


async def test_daily_post_jsonb_roundtrip(session: AsyncSession):
    # 中文注释：验证DailyPost.images/tags 使用 JSONB 后的读写
    author_id = await _ensure_user(session)

    data = DailyPostCreate(
        content="包含中文emoji 😀",
        images=["/a.png", "/b.png"],
        tags=["日常", "测试"]
    )

    post = await DailyPostCRUD.create(session, data, author_user_id=author_id)
    try:
        got = await session.get(type(post), post.id)  # type: ignore
        assert got.images == data.images
        assert got.tags == data.tags
        assert isinstance(got.images, list)
        assert isinstance(got.tags, list)
    finally:
        await _cleanup_daily_post(session, post.id)  # type: ignore
        # optional cleanup user created in this test session
        # await _cleanup_user(session, author_id)

