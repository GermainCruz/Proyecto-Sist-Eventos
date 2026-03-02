import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        return execute_query(
            """SELECT c.id_cotizacion, p.nombre AS proveedor, e.nombre AS evento,
                      c.fecha_generado, c.monto, c.estado, c.descripcion
               FROM cotizacion_proveedor c
               JOIN proveedores p ON c.id_proveedor = p.id_proveedor
               JOIN eventos e ON c.id_evento = e.id_evento
               ORDER BY c.id_cotizacion DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            """SELECT c.id_cotizacion, p.nombre, c.fecha_generado, c.monto, c.estado, c.descripcion
               FROM cotizacion_proveedor c JOIN proveedores p ON c.id_proveedor=p.id_proveedor
               WHERE c.id_evento=%s ORDER BY c.id_cotizacion""",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_cot):
    try:
        return execute_query_one(
            "SELECT id_cotizacion, id_proveedor, id_evento, fecha_generado, monto, estado, descripcion FROM cotizacion_proveedor WHERE id_cotizacion=%s",
            (id_cot,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_proveedor, id_evento, fecha_generado, monto, descripcion):
    try:
        execute_insert(
            "INSERT INTO cotizacion_proveedor (id_proveedor, id_evento, fecha_generado, monto, descripcion) VALUES (%s,%s,%s,%s,%s)",
            (id_proveedor, id_evento, fecha_generado, monto, descripcion)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear cotización: {e}")
        return False

def cambiar_estado(id_cot, nuevo_estado):
    try:
        execute_insert("UPDATE cotizacion_proveedor SET estado=%s WHERE id_cotizacion=%s", (nuevo_estado, id_cot))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_cot, monto, descripcion):
    try:
        execute_insert("UPDATE cotizacion_proveedor SET monto=%s, descripcion=%s WHERE id_cotizacion=%s", (monto, descripcion, id_cot))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_cot):
    try:
        execute_insert("DELETE FROM cotizacion_proveedor WHERE id_cotizacion=%s AND estado='Pendiente'", (id_cot,))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False
