"""Database access layer with connection pooling.

A connection pool keeps a set of open connections ready to be reused,
avoiding the cost of opening a new TCP+auth handshake on every request.
This is the standard production pattern for API backends.
"""
import logging
import os
from pathlib import Path

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("academia360.db")

_DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "academia360"),
    "connection_timeout": 10,
}

_pool: pooling.MySQLConnectionPool | None = None


def _get_pool() -> pooling.MySQLConnectionPool:
    """Lazily create the pool on first use so the app can boot even if
    the database is temporarily unreachable (e.g. Render cold start)."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="academia360_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            pool_reset_session=True,
            **_DB_CONFIG,
        )
        logger.info("MySQL connection pool created (size=%s)", _pool.pool_size)
    return _pool


def get_connection():
    """Borrow a connection from the pool. Falls back to a direct
    connection if the pool is exhausted under burst load."""
    try:
        return _get_pool().get_connection()
    except mysql.connector.errors.PoolError:
        logger.warning("Pool exhausted; opening direct connection")
        return mysql.connector.connect(**_DB_CONFIG)


def get_db():
    """FastAPI dependency: yields a pooled connection and guarantees
    it is returned to the pool (or closed) after the request."""
    connection = get_connection()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
