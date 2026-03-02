import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

ESTADOS_OC = ['Pendiente', 'En Revisión', 'Aprobada', 'Rechazada', 'Enviada', 'Recibida']

def get_all():
    try:
        return execute_query(
            """SELECT oc.id_orden_compra, e.nombre AS evento, p.nombre AS proveedor,
                      r.nombre AS recurso, oc.fecha, oc.estado, oc.monto
               FROM ordenes_compra oc
               JOIN eventos e ON oc.id_evento=e.id_evento
               JOIN proveedores p ON oc.id_proveedor=p.id_proveedor
               JOIN recursos r ON oc.id_recurso=r.id_recurso
               ORDER BY oc.id_orden_compra DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_oc):
    try:
        return execute_query_one(
            "SELECT id_orden_compra, id_evento, id_proveedor, id_recurso, id_cotizacion, fecha, estado, monto FROM ordenes_compra WHERE id_orden_compra=%s",
            (id_oc,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, id_proveedor, id_recurso, id_cotizacion, fecha, monto):
    try:
        execute_insert(
            "INSERT INTO ordenes_compra (id_evento, id_proveedor, id_recurso, id_cotizacion, fecha, monto) VALUES (%s,%s,%s,%s,%s,%s)",
            (id_evento, id_proveedor, id_recurso, id_cotizacion if id_cotizacion else None, fecha, monto)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear OC: {e}")
        return False

def cambiar_estado(id_oc, nuevo_estado):
    try:
        execute_insert("UPDATE ordenes_compra SET estado=%s WHERE id_orden_compra=%s", (nuevo_estado, id_oc))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_oc, monto, estado):
    try:
        execute_insert("UPDATE ordenes_compra SET monto=%s, estado=%s WHERE id_orden_compra=%s", (monto, estado, id_oc))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_oc):
    return cambiar_estado(id_oc, 'Rechazada')
