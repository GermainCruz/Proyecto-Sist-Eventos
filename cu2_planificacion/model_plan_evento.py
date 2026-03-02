import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        return execute_query(
            """SELECT p.id_plan_evento, e.nombre AS evento, p.fecha_elaboracion,
                      p.presupuesto, p.estado, p.descripcion
               FROM plan_evento p JOIN eventos e ON p.id_evento = e.id_evento
               ORDER BY p.id_plan_evento DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            "SELECT id_plan_evento, fecha_elaboracion, presupuesto, estado, descripcion FROM plan_evento WHERE id_evento=%s ORDER BY id_plan_evento DESC",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_plan):
    try:
        return execute_query_one(
            "SELECT id_plan_evento, id_evento, fecha_elaboracion, presupuesto, estado, descripcion FROM plan_evento WHERE id_plan_evento=%s",
            (id_plan,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, fecha_elaboracion, presupuesto, descripcion):
    try:
        execute_insert(
            "INSERT INTO plan_evento (id_evento, fecha_elaboracion, presupuesto, descripcion) VALUES (%s,%s,%s,%s)",
            (id_evento, fecha_elaboracion, presupuesto, descripcion)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear plan: {e}")
        return False

def update(id_plan, fecha_elaboracion, presupuesto, descripcion):
    try:
        execute_insert(
            "UPDATE plan_evento SET fecha_elaboracion=%s, presupuesto=%s, descripcion=%s WHERE id_plan_evento=%s",
            (fecha_elaboracion, presupuesto, descripcion, id_plan)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def cambiar_estado(id_plan, nuevo_estado):
    try:
        execute_insert("UPDATE plan_evento SET estado=%s WHERE id_plan_evento=%s", (nuevo_estado, id_plan))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_plan):
    st.warning("No se pueden eliminar planes; cambiar estado a Rechazado.")
    return False
