import os
from contextlib import contextmanager

import psycopg

from config_runtime import logger

DB_NAME = os.environ.get('PRIMARY_DB_NAME') or os.environ.get('DB_NAME')
DB_USER = os.environ.get('PRIMARY_DB_USER') or os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('PRIMARY_DB_PASSWORD') or os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('PRIMARY_DB_HOST') or os.environ.get('DB_HOST') or '127.0.0.1'
DB_PORT = int(os.environ.get('PRIMARY_DB_PORT') or os.environ.get('DB_PORT') or '5432')

CREATE_SQL = '''
CREATE TABLE IF NOT EXISTS discord_bot_command_events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    command_name TEXT NOT NULL,
    guild_id TEXT,
    channel_id TEXT,
    user_id TEXT,
    username TEXT,
    sport_label TEXT,
    game_label TEXT,
    source TEXT,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    duration_ms INTEGER,
    error_text TEXT
);
CREATE INDEX IF NOT EXISTS discord_bot_command_events_created_at_idx ON discord_bot_command_events (created_at DESC);
CREATE INDEX IF NOT EXISTS discord_bot_command_events_command_idx ON discord_bot_command_events (command_name, created_at DESC);
CREATE INDEX IF NOT EXISTS discord_bot_command_events_guild_idx ON discord_bot_command_events (guild_id, created_at DESC);
'''


def analytics_enabled():
    return all([DB_NAME, DB_USER, DB_PASSWORD])


@contextmanager
def get_conn():
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        autocommit=True,
    )
    try:
        yield conn
    finally:
        conn.close()


def ensure_analytics_table():
    if not analytics_enabled():
        logger.warning('Discord analytics disabled: missing Postgres env vars')
        return
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(CREATE_SQL)
    except Exception as exc:
        logger.warning('Failed to ensure Discord analytics table: %s', exc)


def log_command_event(*, command_name, guild_id=None, channel_id=None, user_id=None, username=None,
                      sport_label=None, game_label=None, source=None, success=True,
                      duration_ms=None, error_text=None):
    if not analytics_enabled():
        return
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO discord_bot_command_events (
                    command_name, guild_id, channel_id, user_id, username,
                    sport_label, game_label, source, success, duration_ms, error_text
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    command_name,
                    guild_id,
                    channel_id,
                    user_id,
                    username,
                    sport_label,
                    game_label,
                    source,
                    success,
                    duration_ms,
                    error_text,
                ),
            )
    except Exception as exc:
        logger.warning('Failed to log Discord analytics event: %s', exc)
