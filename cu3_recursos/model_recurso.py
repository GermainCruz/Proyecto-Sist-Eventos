import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

TIPOS_RECURSO = ['Material', 'Logístico', 'Personal', 'Tecnológico', 'Otro']
ESTADOS_RECURSO = ['Disponible', 'Asignado', 'No Disponible', 'Mantenimiento']

def get_all():
    try:
        return execute_query(
            """SELECT r.id_recurso, r.nombre, r.tipo_recurso, r.cantidad, r.estado,
                      COALESCE(p.nombre,'—') AS proveedor
               FROM recursos r LEFT JOIN proveedores p ON r.id_proveedor=p.id_proveedor
               ORDER BY r.id_recurso"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_recurso):
    try:
        return execute_query_one(
            "SELECT id_recurso, nombre, tipo_recurso, cantidad, estado, id_proveedor FROM recursos WHERE id_recurso=%s",
            (id_recurso,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def get_disponibles_por_tipo(tipo_recurso):
    try:
        return execute_query(
            "SELECT id_recurso, nombre, tipo_recurso, cantidad FROM recursos WHERE estado='Disponible' AND tipo_recurso=%s",
            (tipo_recurso,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def create(nombre, tipo_recurso, cantidad, estado, id_proveedor=None):
    try:
        execute_insert(
            "INSERT INTO recursos (nombre, tipo_recurso, cantidad, estado, id_proveedor) VALUES (%s,%s,%s,%s,%s)",
            (nombre, tipo_recurso, cantidad, estado, id_proveedor)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_recurso, nombre, tipo_recurso, cantidad, estado, id_proveedor=None):
    try:
        execute_insert(
            "UPDATE recursos SET nombre=%s, tipo_recurso=%s, cantidad=%s, estado=%s, id_proveedor=%s WHERE id_recurso=%s",
            (nombre, tipo_recurso, cantidad, estado, id_proveedor, id_recurso)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def cambiar_estado(id_recurso, nuevo_estado):
    try:
        execute_insert("UPDATE recursos SET estado=%s WHERE id_recurso=%s", (nuevo_estado, id_recurso))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_recurso):
    return cambiar_estado(id_recurso, 'No Disponible')
