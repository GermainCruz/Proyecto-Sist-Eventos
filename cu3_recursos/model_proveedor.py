import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert
import streamlit as st

@st.cache_data(ttl=60)
def get_all():
    try:
        return execute_query(
            "SELECT id_proveedor, nombre, tipo_servicio, disponibilidad, email, telefono FROM proveedores ORDER BY nombre"
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_proveedor):
    try:
        return execute_query_one(
            "SELECT id_proveedor, nombre, tipo_servicio, disponibilidad, email, telefono FROM proveedores WHERE id_proveedor=%s",
            (id_proveedor,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(nombre, tipo_servicio, disponibilidad, email, telefono):
    try:
        execute_insert(
            "INSERT INTO proveedores (nombre, tipo_servicio, disponibilidad, email, telefono) VALUES (%s,%s,%s,%s,%s)",
            (nombre, tipo_servicio, disponibilidad, email, telefono)
        )
        get_all.clear()
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear proveedor: {e}")
        return False

def update(id_proveedor, nombre, tipo_servicio, disponibilidad, email, telefono):
    try:
        execute_insert(
            "UPDATE proveedores SET nombre=%s, tipo_servicio=%s, disponibilidad=%s, email=%s, telefono=%s WHERE id_proveedor=%s",
            (nombre, tipo_servicio, disponibilidad, email, telefono, id_proveedor)
        )
        get_all.clear()
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_proveedor):
    try:
        execute_insert("UPDATE proveedores SET disponibilidad=FALSE WHERE id_proveedor=%s", (id_proveedor,))
        get_all.clear()
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False
