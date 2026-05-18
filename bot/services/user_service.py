"""Сервис для работы с пользователями — хранение прогресса."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"


def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)


def _save_users(users: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def get_user(user_id: int) -> dict:
    users = _load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "current_lesson": 0,
            "completed": [],
            "unlocked": False,
            "started_at": None,
        }
        _save_users(users)
    return users[uid]


def update_user(user_id: int, data: dict):
    users = _load_users()
    uid = str(user_id)
    users[uid] = data
    _save_users(users)


def complete_lesson(user_id: int, lesson_id: int):
    user = get_user(user_id)
    if lesson_id not in user["completed"]:
        user["completed"].append(lesson_id)
        user["completed"] = sorted(user["completed"])
        if lesson_id >= user["current_lesson"]:
            user["current_lesson"] = lesson_id + 1
        update_user(user_id, user)
    return user


def unlock_access(user_id: int):
    user = get_user(user_id)
    user["unlocked"] = True
    if not user["started_at"]:
        from datetime import datetime
        user["started_at"] = datetime.now().isoformat()
    update_user(user_id, user)
    return user
