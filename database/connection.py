import psycopg2
from psycopg2 import pool
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

logger = logging.getLogger(__name__)

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        try:
            _pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            
        except psycopg2.Error as e:
            logger.critical(f"Error al crear pool de conexiones: {e}")
            raise
    return _pool

def get_connection():
    return get_pool().getconn()

def release_connection(conn):
    get_pool().putconn(conn)

def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return cur.rowcount
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error en query: {e}")
        raise
    finally:
        release_connection(conn)

def execute_query_one(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    except psycopg2.Error as e:
        logger.error(f"Error en query: {e}")
        raise
    finally:
        release_connection(conn)

def execute_insert(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            if cur.description:
                return cur.fetchone()
            return None
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error en insert: {e}")
        raise
    finally:
        release_connection(conn)
