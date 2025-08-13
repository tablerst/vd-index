import asyncio
import random
import pytest

from sqlmodel import select, func as sf

from services.config.factory import ConfigServiceFactory
from services.database.service import DatabaseService
from services.deps import set_database_service, clear_database_service
from services.auth.service import AuthService
from services.database.models import (
    DailyPostCreate,
    DailyPostUpdate,
    DailyPostCRUD,
)
from services.database.models.user import UserCRUD, UserCreate
from services.database.models.daily_post.base import DailyPost


# NOTE: Comments are in English by project convention.


def _random_pick(arr):
    return arr[random.randint(0, len(arr) - 1)]


def _random_int(min_v, max_v):
    return random.randint(min_v, max_v)


@pytest.mark.asyncio
async def test_insert_30_daily_posts():
    """
    Insert 30 DailyPost rows for testing, referencing frontend mock logic.

    Steps:
    1) Initialize Config and Database services, ensure tables exist.
    2) Create 8 author users if not present.
    3) Insert 30 DailyPost records with randomized content/images/tags.
    4) Randomly set likes/comments via update, and increment views a few times.
    5) Assert total count increased by at least 30.
    """

    # 1) Initialize config and database services
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()

    db_service = DatabaseService(settings.database_url)
    set_database_service(db_service)

    # Ensure tables exist (no-op if already migrated)
    await db_service.create_db_and_tables()

    # Auth service for hashing passwords when creating users
    auth_service = AuthService(settings)

    # Frontend mock data sources
    tags_pool = [
        "旅行", "手工", "上新", "日常", "摄影", "学习", "跑步", "美食",
    ]
    content_types = [
        "今天练了两个小时，进步了一点点～",
        "夏日小集——手工饰品上新喔~",
        "在路上，风很轻，云很白。",
        "复盘：如何稳定 45fps 的渲染表现",
        "拾光：老相机与胶片的味道",
        "跑步第 42 天，5.2km 🏃",
        "平平无奇，但也值得记录的一天",
    ]

    # 2) Create authors (8 users similar to frontend names list size)
    author_usernames = [
        "author_01", "author_02", "author_03", "author_04",
        "author_05", "author_06", "author_07", "author_08",
    ]

    async with db_service.with_session() as session:
        # Record initial count
        initial_total = (await session.exec(select(sf.count()).select_from(DailyPost))).one()

        # Ensure authors exist and collect their IDs
        authors: list[int] = []
        for uname in author_usernames:
            existing = await UserCRUD.get_by_username(session, uname)
            if existing is None:
                # Create new user with hashed password
                password_hash = auth_service.get_password_hash("testpass123")
                user = await UserCRUD.create(
                    session,
                    UserCreate(username=uname, password="testpass123", role="viewer"),
                    password_hash=password_hash,
                )
            else:
                user = existing
            authors.append(user.id)

        # 3) Insert 30 DailyPost records
        for i in range(30):
            has_image = random.random() > 0.3
            img_count = _random_int(1, 3) if has_image else 0
            images = [f"https://picsum.photos/seed/picsum/300/200" for _ in range(img_count)]

            content = _random_pick(content_types) if random.random() > 0.15 else ""
            tag_count = _random_int(0, 3)
            tags = [_random_pick(tags_pool) for _ in range(tag_count)]

            create_payload = DailyPostCreate(
                content=content,
                images=images,
                tags=tags,
                published=True,
            )

            author_user_id = _random_pick(authors)
            post = await DailyPostCRUD.create(session, create_payload, author_user_id=author_user_id)

            # 4) Randomize likes/comments via update (views via small increments)
            likes = _random_int(0, 120)
            comments = _random_int(0, 30)
            await DailyPostCRUD.update(
                session,
                post_id=post.id,
                data=DailyPostUpdate(likes_count=likes, comments_count=comments)
            )

            # Increment views a small random number of times to avoid heavy loops
            for _ in range(_random_int(0, 5)):
                await DailyPostCRUD.increment_views(session, post.id)

        # Verify final count increased by at least 30
        final_total = (await session.exec(select(sf.count()).select_from(DailyPost))).one()
        assert final_total - initial_total >= 30, (
            f"Expected to insert >=30 posts, but count diff was {final_total - initial_total}"
        )

    # Cleanup database service handle in deps (optional for test isolation)
    clear_database_service()

