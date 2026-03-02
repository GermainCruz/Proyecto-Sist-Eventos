import bcrypt
import psycopg2
import logging
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

logger = logging.getLogger(__name__)

def get_all():
    try:
        rows = execute_query(
            "SELECT id_usuario, nombre, apellido, email, user_login, rol, estado, created_at FROM usuarios ORDER BY id_usuario"
        )
        return rows or []
    except psycopg2.Error as e:
        st.error(f"Error al obtener usuarios: {e}")
        return []

def get_by_id(id_usuario):
    try:
        return execute_query_one(
            "SELECT id_usuario, nombre, apellido, email, user_login, rol, estado FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )
    except psycopg2.Error as e:
        st.error(f"Error al obtener usuario: {e}")
        return None

def create(nombre, apellido, email, user_login, password, rol):
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
        execute_insert(
            """INSERT INTO usuarios (nombre, apellido, email, user_login, password_hash, rol)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, apellido, email, user_login, hashed, rol)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear usuario: {e}")
        return False

def update(id_usuario, nombre, apellido, email, rol, estado):
    try:
        execute_insert(
            """UPDATE usuarios SET nombre=%s, apellido=%s, email=%s, rol=%s, estado=%s
               WHERE id_usuario=%s""",
            (nombre, apellido, email, rol, estado, id_usuario)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al actualizar usuario: {e}")
        return False

def update_password(id_usuario, new_password):
    try:
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()
        execute_insert(
            "UPDATE usuarios SET password_hash=%s WHERE id_usuario=%s",
            (hashed, id_usuario)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al cambiar contraseña: {e}")
        return False

def delete(id_usuario):
    try:
        execute_insert("UPDATE usuarios SET estado='Inactivo' WHERE id_usuario=%s", (id_usuario,))
        return True
    except psycopg2.Error as e:
        st.error(f"Error al eliminar usuario: {e}")
        return False
