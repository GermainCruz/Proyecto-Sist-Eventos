import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

def get_all():
    try:
        rows = execute_query(
            """SELECT c.id_contrato, c.nro_contrato, e.nombre AS evento,
                      p.nombre AS proveedor, c.fecha_contrato,
                      c.estado_contrato, c.monto, c.firma_digital
               FROM contratos c
               JOIN eventos e ON c.id_evento = e.id_evento
               JOIN proveedores p ON c.id_proveedor = p.id_proveedor
               ORDER BY c.id_contrato DESC"""
        )
        return rows or []
    except psycopg2.Error as e:
        st.error(f"Error al obtener contratos: {e}")
        return []

def get_by_id(id_contrato):
    try:
        return execute_query_one(
            """SELECT c.id_contrato, c.nro_contrato, c.id_evento, c.id_proveedor,
                      c.fecha_contrato, c.estado_contrato, c.monto,
                      c.descripcion, c.firma_digital
               FROM contratos c WHERE c.id_contrato = %s""",
            (id_contrato,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def get_by_evento(id_evento):
    try:
        return execute_query(
            """SELECT id_contrato, nro_contrato, estado_contrato, monto, firma_digital
               FROM contratos WHERE id_evento=%s ORDER BY id_contrato""",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_next_correlativo():
    try:
        row = execute_query_one("SELECT COUNT(*) + 1 FROM contratos")
        return row[0] if row else 1
    except:
        return 1

def create(nro_contrato, id_evento, id_proveedor, fecha_contrato, monto, descripcion, firma_digital):
    try:
        execute_insert(
            """INSERT INTO contratos (nro_contrato, id_evento, id_proveedor, fecha_contrato, monto, descripcion, firma_digital)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (nro_contrato, id_evento, id_proveedor, fecha_contrato, monto, descripcion, firma_digital)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al crear contrato: {e}")
        return False

def update(id_contrato, monto, descripcion, fecha_contrato, firma_digital):
    try:
        execute_insert(
            "UPDATE contratos SET monto=%s, descripcion=%s, fecha_contrato=%s, firma_digital=%s WHERE id_contrato=%s",
            (monto, descripcion, fecha_contrato, firma_digital, id_contrato)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al actualizar: {e}")
        return False

def cambiar_estado(id_contrato, nuevo_estado):
    try:
        execute_insert(
            "UPDATE contratos SET estado_contrato=%s WHERE id_contrato=%s AND estado_contrato='Pendiente'",
            (nuevo_estado, id_contrato)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al cambiar estado: {e}")
        return False

def confirmar_cumplimiento(id_contrato):
    try:
        execute_insert(
            "UPDATE contratos SET estado_contrato='Cumplido' WHERE id_contrato=%s",
            (id_contrato,)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_contrato):
    st.warning("Los contratos no se eliminan; cambia su estado.")
    return False
