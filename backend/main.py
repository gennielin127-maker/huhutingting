from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            date TEXT PRIMARY KEY,
            mood_f TEXT,
            mood_m TEXT,
            updated_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS memories (
            id BIGINT PRIMARY KEY,
            date TEXT,
            title TEXT,
            icon TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS wishes (
            id BIGINT PRIMARY KEY,
            title TEXT,
            cat TEXT,
            date TEXT,
            done BOOLEAN DEFAULT FALSE,
            done_date TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS fights (
            id BIGINT PRIMARY KEY,
            date TEXT,
            topics TEXT,
            fault TEXT,
            resolved TEXT,
            score INTEGER DEFAULT 0,
            note TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
except:
    pass

# ── Moods ──
class MoodIn(BaseModel):
    date: str
    mood_f: str
    mood_m: str

@app.get("/moods")
def get_moods():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM moods ORDER BY date DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return list(rows)

@app.post("/moods")
def save_mood(data: MoodIn):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO moods (date, mood_f, mood_m, updated_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (date) DO UPDATE SET mood_f=EXCLUDED.mood_f, mood_m=EXCLUDED.mood_m, updated_at=NOW()
    """, (data.date, data.mood_f, data.mood_m))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ── Memories ──
class MemoryIn(BaseModel):
    id: int
    date: str
    title: str
    icon: str
    note: Optional[str] = ""

@app.get("/memories")
def get_memories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memories ORDER BY date DESC, id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return list(rows)

@app.post("/memories")
def save_memory(data: MemoryIn):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO memories (id, date, title, icon, note)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (data.id, data.date, data.title, data.icon, data.note))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/memories/{mid}")
def delete_memory(mid: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM memories WHERE id=%s", (mid,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ── Wishes ──
class WishIn(BaseModel):
    id: int
    title: str
    cat: str
    date: str
    done: bool = False
    done_date: Optional[str] = None

@app.get("/wishes")
def get_wishes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wishes ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return list(rows)

@app.post("/wishes")
def save_wish(data: WishIn):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO wishes (id, title, cat, date, done, done_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET done=EXCLUDED.done, done_date=EXCLUDED.done_date
    """, (data.id, data.title, data.cat, data.date, data.done, data.done_date))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/wishes/{wid}")
def delete_wish(wid: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM wishes WHERE id=%s", (wid,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ── Fights ──
class FightIn(BaseModel):
    id: int
    date: str
    topics: str
    fault: Optional[str] = None
    resolved: Optional[str] = None
    score: int = 0
    note: Optional[str] = ""

@app.get("/fights")
def get_fights():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fights ORDER BY date DESC, id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return list(rows)

@app.post("/fights")
def save_fight(data: FightIn):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fights (id, date, topics, fault, resolved, score, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (data.id, data.date, data.topics, data.fault, data.resolved, data.score, data.note))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/fights/{fid}")
def delete_fight(fid: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM fights WHERE id=%s", (fid,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}
