"""
QQ group members fetcher (async)
中文注释：从 services/qq_group/fetcher.py 迁移至 utils.qq_group.fetcher。
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import time
import httpx
import re

DEFAULT_BASE_URL = "https://qun.qq.com/cgi-bin/qun_mgr/search_group_members"

class QQGroupFetcherError(Exception):
    """Raised when fetching QQ group members fails."""

async def fetch_members(
    *,
    group_id: str,
    cookie: str,
    bkn: str,
    user_agent: str = "Apifox/1.0.0 (https://apifox.com)",
    page_size: int = 10,
    request_delay: float = 0.5,
    base_url: str = DEFAULT_BASE_URL,
    timeout_s: float = 20.0,
) -> Dict[str, Any]:
    """
    Fetch all members from QQ group by paging and return normalized result.
    Returns a dict similar to original script output: { ec, em, mems, count, ... }.

    注意：
    - 需要合法的 cookie 与 bkn 参数
    - 不在服务端持久化文件，直接返回结果
    """

    cookie_sanitized = re.sub(r"\s+", " ", cookie or "").strip()
    user_agent_sanitized = (user_agent or "Apifox/1.0.0 (https://apifox.com)").strip()

    headers = {
        "Cookie": cookie_sanitized,
        "User-Agent": user_agent_sanitized,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://qun.qq.com",
        "Referer": "https://qun.qq.com/",
    }
    params = {
        "bkn": bkn,
        "ts": str(int(time.time() * 1000)),
    }

    async with httpx.AsyncClient(timeout=timeout_s) as client:
        all_members = []
        start = 0
        total_count: Optional[int] = None
        levelname: Dict[str, Any] = {}
        last_page_data: Optional[Dict[str, Any]] = None

        while True:
            end = start + page_size - 1
            data = {
                "st": str(start),
                "end": str(end),
                "sort": "1",
                "gc": group_id,
                "group_id": group_id,
                "bkn": bkn,
            }

            try:
                resp = await client.post(base_url, headers=headers, params=params, data=data)
            except httpx.RequestError as e:
                raise QQGroupFetcherError(f"Request failed: {e}") from e

            if resp.status_code != 200:
                raise QQGroupFetcherError(f"HTTP {resp.status_code}: {resp.text[:200]}")

            try:
                page_data = resp.json()
            except Exception as e:
                raise QQGroupFetcherError(f"Invalid JSON: {e}") from e

            last_page_data = page_data
            if not page_data or page_data.get("ec", -1) != 0:
                err = page_data.get("em", "unknown error") if isinstance(page_data, dict) else "unknown error"
                raise QQGroupFetcherError(f"API error: ec={page_data.get('ec')}, em={err}")

            if total_count is None:
                total_count = page_data.get("count", 0)
                levelname = page_data.get("levelname", {}) or {}

            current_members = page_data.get("mems", []) or []
            if not current_members:
                break

            all_members.extend(current_members)

            if len(all_members) >= total_count:
                break

            start = end + 1
            if request_delay > 0:
                import asyncio
                await asyncio.sleep(request_delay)

        result = {
            "ec": 0,
            "errcode": 0,
            "em": "",
            "cache": 0,
            "adm_num": last_page_data.get("adm_num", 0) if last_page_data else 0,
            "levelname": levelname,
            "mems": all_members,
            "count": len(all_members),
            "total_count": total_count or len(all_members),
            "svr_time": int(time.time()),
            "max_count": last_page_data.get("max_count", 200) if last_page_data else 200,
            "search_count": len(all_members),
            "extmode": 0,
        }
        return result

