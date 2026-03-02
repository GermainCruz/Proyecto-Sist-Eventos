import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        rows = execute_query(
            "SELECT id_cliente, nombre, tipo_cliente, direccion, email, telefono, fecha_registro, estado FROM clientes ORDER BY id_cliente"
        )
        return rows or []
    except psycopg2.Error as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def get_by_id(id_cliente):
    try:
        return execute_query_one(
            "SELECT id_cliente, nombre, tipo_cliente, direccion, email, telefono, estado FROM clientes WHERE id_cliente = %s",
            (id_cliente,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def search(texto):
    try:
        rows = execute_query(
            "SELECT id_cliente, nombre, tipo_cliente, email, telefono, estado FROM clientes WHERE nombre ILIKE %s OR email ILIKE %s ORDER BY nombre",
            (f"%{texto}%", f"%{texto}%")
        )
        return rows or []
    except psycopg2.Error as e:
        st.error(f"Error al buscar clientes: {e}")
        return []

def create(nombre, tipo_cliente, direccion, email, telefono):
    try:
        execute_insert(
            "INSERT INTO clientes (nombre, tipo_cliente, direccion, email, telefono) VALUES (%s,%s,%s,%s,%s)",
            (nombre, tipo_cliente, direccion, email, telefono)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear cliente: {e}")
        return False

def update(id_cliente, nombre, tipo_cliente, direccion, email, telefono, estado):
    try:
        execute_insert(
            "UPDATE clientes SET nombre=%s, tipo_cliente=%s, direccion=%s, email=%s, telefono=%s, estado=%s WHERE id_cliente=%s",
            (nombre, tipo_cliente, direccion, email, telefono, estado, id_cliente)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al actualizar cliente: {e}")
        return False

def toggle_estado(id_cliente):
    try:
        execute_insert(
            "UPDATE clientes SET estado = CASE estado WHEN 'Activo' THEN 'Inactivo' ELSE 'Activo' END WHERE id_cliente=%s",
            (id_cliente,)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_cliente):
    return toggle_estado(id_cliente)

def get_activos():
    try:
        return execute_query("SELECT id_cliente, nombre, email FROM clientes WHERE estado='Activo' ORDER BY nombre") or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []
