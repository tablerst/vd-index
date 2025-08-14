#!/usr/bin/env python3
"""
Clean up legacy stringified JSON values in JSONB columns for Activities and DailyPosts.
- activities.participant_ids: ensure JSONB array of integers
- activities.tags: ensure JSONB array
- daily_posts.images: ensure JSONB array
- daily_posts.tags: ensure JSONB array

The script reads DATABASE_URL via ConfigService (env .env) and uses DatabaseService.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys

# Ensure backend package imports work when running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import text

from services.config.factory import ConfigServiceFactory
from services.database.factory import DatabaseServiceFactory


async def cleanup() -> None:
    # Load settings
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()

    # Init DB service
    db_factory = DatabaseServiceFactory()
    db = db_factory.create(settings.database_url)

    async with db.with_session() as session:
        # --- Pass 1: Convert stringified arrays to actual JSONB arrays ---
        # Activities.participant_ids
        q1_count = text(
            """
            SELECT COUNT(*) AS c
            FROM activities
            WHERE jsonb_typeof(participant_ids) = 'string'
              AND (participant_ids #>> '{}') LIKE '[%]'
            """
        )
        c1 = (await session.exec(q1_count)).one()
        if c1:
            upd1 = text(
                """
                UPDATE activities
                SET participant_ids = (participant_ids #>> '{}')::jsonb
                WHERE jsonb_typeof(participant_ids) = 'string'
                  AND (participant_ids #>> '{}') LIKE '[%]'
                """
            )
            await session.exec(upd1)
            await session.commit()
            print(f"activities.participant_ids: converted stringified arrays -> JSONB arrays, rows: {c1}")

        # Activities.tags
        q2_count = text(
            """
            SELECT COUNT(*) AS c
            FROM activities
            WHERE jsonb_typeof(tags) = 'string'
              AND (tags #>> '{}') LIKE '[%]'
            """
        )
        c2 = (await session.exec(q2_count)).one()
        if c2:
            upd2 = text(
                """
                UPDATE activities
                SET tags = (tags #>> '{}')::jsonb
                WHERE jsonb_typeof(tags) = 'string'
                  AND (tags #>> '{}') LIKE '[%]'
                """
            )
            await session.exec(upd2)
            await session.commit()
            print(f"activities.tags: converted stringified arrays -> JSONB arrays, rows: {c2}")

        # DailyPosts.images
        q3_count = text(
            """
            SELECT COUNT(*) AS c
            FROM daily_posts
            WHERE jsonb_typeof(images) = 'string'
              AND (images #>> '{}') LIKE '[%]'
            """
        )
        c3 = (await session.exec(q3_count)).one()
        if c3:
            upd3 = text(
                """
                UPDATE daily_posts
                SET images = (images #>> '{}')::jsonb
                WHERE jsonb_typeof(images) = 'string'
                  AND (images #>> '{}') LIKE '[%]'
                """
            )
            await session.exec(upd3)
            await session.commit()
            print(f"daily_posts.images: converted stringified arrays -> JSONB arrays, rows: {c3}")

        # DailyPosts.tags
        q4_count = text(
            """
            SELECT COUNT(*) AS c
            FROM daily_posts
            WHERE jsonb_typeof(tags) = 'string'
              AND (tags #>> '{}') LIKE '[%]'
            """
        )
        c4 = (await session.exec(q4_count)).one()
        if c4:
            upd4 = text(
                """
                UPDATE daily_posts
                SET tags = (tags #>> '{}')::jsonb
                WHERE jsonb_typeof(tags) = 'string'
                  AND (tags #>> '{}') LIKE '[%]'
                """
            )
            await session.exec(upd4)
            await session.commit()
            print(f"daily_posts.tags: converted stringified arrays -> JSONB arrays, rows: {c4}")

        # --- Pass 2: Normalize participant_ids array elements to integers when possible ---
        # Convert string numeric elements to integers
        q5_count = text(
            """
            SELECT COUNT(*) AS c
            FROM activities
            WHERE jsonb_typeof(participant_ids) = 'array'
              AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(participant_ids) AS elem
                WHERE jsonb_typeof(elem) = 'string'
              )
            """
        )
        c5 = (await session.exec(q5_count)).one()
        if c5:
            upd5 = text(
                """
                UPDATE activities
                SET participant_ids = (
                  SELECT jsonb_agg(
                           CASE
                             WHEN jsonb_typeof(elem) = 'string' AND (elem #>> '{}') ~ '^[0-9]+$'
                               THEN to_jsonb(((elem #>> '{}')::int))
                             ELSE elem
                           END
                         )
                  FROM jsonb_array_elements(participant_ids) AS elem
                )
                WHERE jsonb_typeof(participant_ids) = 'array'
                  AND EXISTS (
                    SELECT 1 FROM jsonb_array_elements(participant_ids) AS elem
                    WHERE jsonb_typeof(elem) = 'string'
                  )
                """
            )
            await session.exec(upd5)
            await session.commit()
            print(f"activities.participant_ids: normalized string elements to integers when possible, rows: {c5}")

        print("✅ Cleanup completed.")


if __name__ == "__main__":
    asyncio.run(cleanup())

