"""База данных SQLite для MOTioN HABITAR."""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'motion.db')


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            unlocked BOOLEAN DEFAULT 0,
            payment_id TEXT,
            joined_at TEXT,
            last_active TEXT
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            description TEXT,
            price_promo INTEGER,
            price_regular INTEGER,
            mercadopago_link TEXT,
            active BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL REFERENCES courses(id),
            lesson_order INTEGER NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            intro TEXT,
            reflection TEXT,
            video_url TEXT,
            video_type TEXT DEFAULT 'youtube',
            duration TEXT,
            feel_tags TEXT,
            UNIQUE(course_id, lesson_order)
        );

        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER NOT NULL REFERENCES users(id),
            lesson_id INTEGER NOT NULL REFERENCES lessons(id),
            completed_at TEXT,
            reflection_text TEXT,
            PRIMARY KEY (user_id, lesson_id)
        );
    """)
    conn.commit()

    # Seed default course if empty
    cnt = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if cnt == 0:
        conn.execute("""
            INSERT INTO courses (slug, title, subtitle, description, price_promo, price_regular, mercadopago_link)
            VALUES ('habitar', 'HABITAR', 'Un recorrido para volver a conectar con tu cuerpo',
                    'Cuatro experiencias de movimiento consciente disenadas para acompanarte de vuelta a tu cuerpo. Sin exigencia, sin velocidad. Solo presencia.',
                    29000, 45000, 'https://mpago.li/29UE9Le')
        """)
        course_id = conn.execute("SELECT id FROM courses WHERE slug='habitar'").fetchone()[0]

        lessons = [
            (course_id, 1, 'PAUSAR', 'En la pausa también existe movimiento.',
             'El cuerpo habla cuando hacemos silencio.\n\nEn esta primera experiencia, nos detenemos. Sin prisa, sin exigencia. Solo observar lo que ya está acá.\n\nNo hay nada que hacer. Solo estar.',
             'Después de esta pausa...\n\n¿Qué sensación queda en tu cuerpo ahora?\n¿Hubo un momento en que te costó quedarte quieta?',
             'https://www.youtube.com/embed/fYJSY1ErPU4?rel=0&modestbranding=1&controls=1&disablekb=1',
             'youtube', '22 min', 'Calma · Quietud · Escucha'),
            (course_id, 2, 'LIBERAR', 'No todo lo que sostengo me pertenece.',
             'Cuánto cargamos sin darnos cuenta.\n\nEsta experiencia es para soltar. Movimientos suaves que abren espacio donde había tensión. Dejar ir lo que ya no es necesario.\n\nTu cuerpo sabe soltar. Solo necesita permiso.',
             'Después de soltar...\n\n¿Sentís alguna parte más liviana?\n¿Dónde estaba acumulada la tensión sin que lo notaras?',
             'https://www.youtube.com/embed/nWs_dkFTKHk?rel=0&modestbranding=1&controls=1&disablekb=1',
             'youtube', '25 min', 'Alivio · Expansión · Suavidad'),
            (course_id, 3, 'FLUIR', '¿Qué ritmo adoptaría mi cuerpo si me permito soltar el control?',
             'Ahora que hay espacio, el movimiento encuentra su curso natural.\n\nEn FLUIR entramos en un ritmo propio. Sin forzar, sin imitar. Movimientos que nacen del centro y se expanden.\n\nDejá que el cuerpo te lleve.',
             'Después de fluir...\n\n¿En qué momento sentiste que tu cuerpo se movía solo?\n¿Apareció alguna resistencia? ¿Qué hiciste con ella?',
             'https://www.youtube.com/embed/fojD7KyKJck?rel=0&modestbranding=1&controls=1&disablekb=1',
             'youtube', '28 min', 'Liviandad · Ritmo · Libertad'),
            (course_id, 4, 'HABITAR', 'El cuerpo como hogar, no como proyecto.',
             'Has llegado.\n\nPAUSASTE. SOLTASTE. FLUISTE.\n\nAhora HABITAR es la integración de todo. Una práctica para quedarte. Para sentir que tu cuerpo no es un proyecto, es un hogar.\n\nEsta experiencia no termina cuando termina la clase. Se queda con vos.',
             'Después de habitar...\n\n¿Cómo se siente estar en tu cuerpo ahora?\nSi tu cuerpo pudiera decirte algo, ¿qué te diría?',
             None, 'youtube', '30 min', 'Presencia · Pertenencia · Plenitud'),
        ]
        conn.executemany("""
            INSERT INTO lessons (course_id, lesson_order, title, subtitle, intro, reflection, video_url, video_type, duration, feel_tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, lessons)
        conn.commit()

    conn.close()


# Helpers

def get_or_create_user(user_id: int, username: str = None, first_name: str = None) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO users (id, username, first_name, joined_at, last_active) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name,
             datetime.now(timezone.utc).isoformat(),
             datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    else:
        conn.execute("UPDATE users SET last_active = ?, username = COALESCE(?, username), first_name = COALESCE(?, first_name) WHERE id = ?",
                     (datetime.now(timezone.utc).isoformat(), username, first_name, user_id))
        conn.commit()
    conn.close()
    return dict(row)


def unlock_user(user_id: int, payment_id: str = None):
    conn = get_db()
    conn.execute("UPDATE users SET unlocked = 1, payment_id = COALESCE(?, payment_id) WHERE id = ?",
                 (payment_id, user_id))
    conn.commit()
    conn.close()


def get_lessons_for_course(course_slug: str = 'habitar') -> list:
    conn = get_db()
    rows = conn.execute("""
        SELECT l.* FROM lessons l
        JOIN courses c ON l.course_id = c.id
        WHERE c.slug = ? AND c.active = 1
        ORDER BY l.lesson_order
    """, (course_slug,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_progress(user_id: int, course_slug: str = 'habitar') -> list:
    conn = get_db()
    rows = conn.execute("""
        SELECT p.lesson_id, p.completed_at, l.title, l.lesson_order
        FROM progress p
        JOIN lessons l ON p.lesson_id = l.id
        JOIN courses c ON l.course_id = c.id
        WHERE p.user_id = ? AND c.slug = ?
        ORDER BY l.lesson_order
    """, (user_id, course_slug)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def complete_lesson_db(user_id: int, lesson_id: int, reflection_text: str = None):
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO progress (user_id, lesson_id, completed_at, reflection_text)
        VALUES (?, ?, ?, ?)
    """, (user_id, lesson_id, datetime.now(timezone.utc).isoformat(), reflection_text))
    conn.commit()
    conn.close()


def get_course(slug: str = 'habitar') -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM courses WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None
