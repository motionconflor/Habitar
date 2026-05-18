"""Загрузка и доступ к урокам."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_lessons() -> list[dict]:
    path = DATA_DIR / "lessons.json"
    with open(path) as f:
        return json.load(f)


def get_lesson(lesson_id: int) -> dict | None:
    lessons = load_lessons()
    for lesson in lessons:
        if lesson["id"] == lesson_id:
            return lesson
    return None


def get_total_lessons() -> int:
    return len(load_lessons())


def get_lesson_title(lesson_id: int) -> str:
    lesson = get_lesson(lesson_id)
    return lesson["title"] if lesson else "—"
