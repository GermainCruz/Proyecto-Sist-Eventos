import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        return execute_query(
            """SELECT i.id_incidencia, e.nombre AS evento, i.tipo_incidencia,
                      i.descripcion, i.fecha_registro, i.estado
               FROM incidencias i JOIN eventos e ON i.id_evento=e.id_evento
               ORDER BY i.id_incidencia DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            "SELECT id_incidencia, tipo_incidencia, descripcion, fecha_registro, estado FROM incidencias WHERE id_evento=%s ORDER BY id_incidencia DESC",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_inc):
    try:
        return execute_query_one(
            "SELECT id_incidencia, id_evento, tipo_incidencia, descripcion, fecha_registro, estado FROM incidencias WHERE id_incidencia=%s",
            (id_inc,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, tipo_incidencia, descripcion):
    try:
        execute_insert(
            "INSERT INTO incidencias (id_evento, tipo_incidencia, descripcion) VALUES (%s,%s,%s)",
            (id_evento, tipo_incidencia, descripcion)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al registrar incidencia: {e}")
        return False

def create_detalle(id_incidencia, descripcion, accion_tomada):
    try:
        execute_insert(
            "INSERT INTO detalle_incidencia (id_incidencia, descripcion, accion_tomada) VALUES (%s,%s,%s)",
            (id_incidencia, descripcion, accion_tomada)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al registrar detalle: {e}")
        return False

def get_detalles(id_incidencia):
    try:
        return execute_query(
            "SELECT id_detalle_incidencia, descripcion, accion_tomada, created_at FROM detalle_incidencia WHERE id_incidencia=%s ORDER BY id_detalle_incidencia",
            (id_incidencia,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def cambiar_estado(id_inc, nuevo_estado):
    try:
        execute_insert("UPDATE incidencias SET estado=%s WHERE id_incidencia=%s", (nuevo_estado, id_inc))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_inc, tipo_incidencia, descripcion):
    try:
        execute_insert("UPDATE incidencias SET tipo_incidencia=%s, descripcion=%s WHERE id_incidencia=%s",
                       (tipo_incidencia, descripcion, id_inc))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_inc):
    return cambiar_estado(id_inc, 'Cerrada')
