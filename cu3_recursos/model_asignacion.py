import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        return execute_query(
            """SELECT a.id_asignacion, e.nombre AS evento, r.nombre AS recurso,
                      a.cantidad, a.fecha_asignacion, a.estado
               FROM asignacion_recurso a
               JOIN eventos e ON a.id_evento=e.id_evento
               JOIN recursos r ON a.id_recurso=r.id_recurso
               ORDER BY a.id_asignacion DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            """SELECT a.id_asignacion, r.nombre, a.cantidad, a.fecha_asignacion, a.estado
               FROM asignacion_recurso a JOIN recursos r ON a.id_recurso=r.id_recurso
               WHERE a.id_evento=%s ORDER BY a.id_asignacion""",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_asignacion):
    try:
        return execute_query_one(
            "SELECT id_asignacion, id_evento, id_recurso, cantidad, fecha_asignacion, estado FROM asignacion_recurso WHERE id_asignacion=%s",
            (id_asignacion,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, id_recurso, cantidad, fecha_asignacion):
    try:
        execute_insert(
            "INSERT INTO asignacion_recurso (id_evento, id_recurso, cantidad, fecha_asignacion) VALUES (%s,%s,%s,%s)",
            (id_evento, id_recurso, cantidad, fecha_asignacion)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def cambiar_estado(id_asignacion, nuevo_estado):
    try:
        execute_insert("UPDATE asignacion_recurso SET estado=%s WHERE id_asignacion=%s", (nuevo_estado, id_asignacion))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_asignacion, cantidad, fecha_asignacion, estado):
    try:
        execute_insert(
            "UPDATE asignacion_recurso SET cantidad=%s, fecha_asignacion=%s, estado=%s WHERE id_asignacion=%s",
            (cantidad, fecha_asignacion, estado, id_asignacion)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_asignacion):
    return cambiar_estado(id_asignacion, 'Cancelada')
