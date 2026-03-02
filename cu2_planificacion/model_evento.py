import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert
from config import ESTADOS_EVENTO

def get_all():
    try:
        rows = execute_query(
            """SELECT e.id_evento, e.nombre, e.tipo_evento, e.lugar_evento,
                      e.fecha_evento, e.monto_evento, e.estado, c.nombre AS cliente
               FROM eventos e JOIN clientes c ON e.id_cliente = c.id_cliente
               ORDER BY e.id_evento DESC"""
        )
        return rows or []
    except psycopg2.Error as e:
        st.error(f"Error al obtener eventos: {e}")
        return []

def get_activos():
    try:
        return execute_query(
            "SELECT id_evento, nombre, estado FROM eventos WHERE estado NOT IN ('Cerrada','Cancelada') ORDER BY nombre"
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_evento):
    try:
        return execute_query_one(
            "SELECT id_evento, nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, estado, id_cliente FROM eventos WHERE id_evento=%s",
            (id_evento,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, id_cliente):
    try:
        execute_insert(
            "INSERT INTO eventos (nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, id_cliente) VALUES (%s,%s,%s,%s,%s,%s)",
            (nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, id_cliente)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear evento: {e}")
        return False

def update(id_evento, nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento):
    try:
        execute_insert(
            "UPDATE eventos SET nombre=%s, tipo_evento=%s, lugar_evento=%s, fecha_evento=%s, monto_evento=%s WHERE id_evento=%s",
            (nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, id_evento)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def cambiar_estado(id_evento, nuevo_estado):
    try:
        execute_insert("UPDATE eventos SET estado=%s WHERE id_evento=%s", (nuevo_estado, id_evento))
        return True
    except psycopg2.Error as e:
        st.error(f"Error al cambiar estado: {e}")
        return False

def delete(id_evento):
    try:
        execute_insert("UPDATE eventos SET estado='Cancelada' WHERE id_evento=%s", (id_evento,))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False
