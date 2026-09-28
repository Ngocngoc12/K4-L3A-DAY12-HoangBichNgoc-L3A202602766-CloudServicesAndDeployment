"""CP4 -- Stateless: state song ngoai process.

Neu lich su hoi thoai nam trong mot dict trong RAM, thi khi scale len 3
instance, user hoi cau 1 vao instance A va cau 2 vao instance B se thay agent
"mat tri nho". Container con bi restart bat cu luc nao. Vi vay state phai
nam o noi moi instance cung nhin thay: Redis.
"""

from __future__ import annotations

import json

import redis

from .config import get_settings

HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 7 * 24 * 3600


def get_redis_client(url: str | None = None):
    """CHO SAN -- tao client Redis tu URL.

    ``fake://`` tra ve Redis gia chay trong RAM, dung khi may ban chua co
    Docker. Tien cho luc hoc, nhung KHONG dung khi deploy: no van la state
    trong process, dung cai ma CP4 dang tim cach loai bo.
    """
    url = url or get_settings().redis_url
    if url.startswith("fake://"):
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    return redis.from_url(url, decode_responses=True)


class ConversationStore:
    """Luu lich su hoi thoai cua tung user trong Redis List."""

    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(user_id: str) -> str:
        """CHO SAN."""
        return f"history:{user_id}"

    def ping(self) -> bool:
        """Redis co tra loi khong? Dung cho endpoint /ready."""
        try:
            return self.client.ping()
        except Exception:
            return False

    def append(self, user_id: str, role: str, content: str) -> None:
        """Ghi them mot luot vao lich su."""
        key = self._key(user_id)
        msg = json.dumps({"role": role, "content": content}, ensure_ascii=False)
        self.client.rpush(key, msg)
        self.client.ltrim(key, -HISTORY_MAX_MESSAGES, -1)
        self.client.expire(key, HISTORY_TTL_SECONDS)

    def get_history(self, user_id: str) -> list[dict]:
        """Doc lich su hoi thoai, cu nhat truoc."""
        key = self._key(user_id)
        raw_items = self.client.lrange(key, 0, -1)
        return [json.loads(item) for item in raw_items]

    def clear(self, user_id: str) -> None:
        """CHO SAN -- xoa lich su cua mot user."""
        self.client.delete(self._key(user_id))
