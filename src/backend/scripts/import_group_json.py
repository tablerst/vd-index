
import json
import secrets
from pathlib import Path
import asyncio

from sqlmodel import SQLModel, Session, create_engine, delete

from models.models import Member
from core.crypto import encrypt_uin
from core.config import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

async def import_members(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    members = []
    for item in data:
        salt = secrets.token_hex(8)  # 8 byte hex
        uin_enc = encrypt_uin(item["uin"], salt)
        members.append(
            Member(
                display_name=item.get("card") or item.get("nick"),
                group_nick=item.get("card"),
                qq_nick=item.get("nick"),
                role=item["role"],
                uin_encrypted=uin_enc,
                salt=salt,
                salt=salt,
                salt=salt,
                join_time=item["join_time"],
                last_speak_time=item["last_speak_time"],
                level_point=item["lv"]["point"],
                level_value=item["lv"]["level"],
                tags=item["tags"],
                flag=item["flag"],
                q_age=item["qage"],
                rm=item["rm"],
            )
        )

    # 使用 AsyncSession(engine) as sess
    async with Session(engine) as sess:
        await sess.execute(delete(Member))
        await sess.commit()
        sess.add_all(members)
        await sess.commit()
        # ...existing code...

if __name__ == "__main__":
    # Example usage: asyncio.run(import_members(Path("group.json")))
    pass
