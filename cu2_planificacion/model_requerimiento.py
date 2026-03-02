import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

TIPOS_RECURSO = ['Material', 'Logístico', 'Personal', 'Tecnológico', 'Otro']

def get_by_evento(id_evento):
    try:
        return execute_query(
            "SELECT id_requerimiento, descripcion, tipo_recurso, cantidad FROM requerimientos_evento WHERE id_evento=%s ORDER BY id_requerimiento",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_req):
    try:
        return execute_query_one(
            "SELECT id_requerimiento, id_evento, descripcion, tipo_recurso, cantidad FROM requerimientos_evento WHERE id_requerimiento=%s",
            (id_req,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, descripcion, tipo_recurso, cantidad):
    try:
        execute_insert(
            "INSERT INTO requerimientos_evento (id_evento, descripcion, tipo_recurso, cantidad) VALUES (%s,%s,%s,%s)",
            (id_evento, descripcion, tipo_recurso, cantidad)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear requerimiento: {e}")
        return False

def update(id_req, descripcion, tipo_recurso, cantidad):
    try:
        execute_insert(
            "UPDATE requerimientos_evento SET descripcion=%s, tipo_recurso=%s, cantidad=%s WHERE id_requerimiento=%s",
            (descripcion, tipo_recurso, cantidad, id_req)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_req):
    try:
        execute_insert("DELETE FROM requerimientos_evento WHERE id_requerimiento=%s", (id_req,))
        return True
    except psycopg2.Error as e:
        st.error(f"Error al eliminar: {e}")
        return False

def get_all():
    try:
        return execute_query("SELECT id_requerimiento, id_evento, descripcion, tipo_recurso, cantidad FROM requerimientos_evento ORDER BY id_requerimiento") or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []
