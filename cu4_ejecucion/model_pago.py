import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

TIPOS_PAGO = ['Normal', 'Adicional', 'Restante']

def get_all():
    try:
        return execute_query(
            """SELECT p.id_pago, e.nombre AS evento, COALESCE(c.nro_contrato,'—') AS contrato,
                      p.tipo_pago, p.monto, p.fecha_pago, p.estado
               FROM pagos p
               JOIN eventos e ON p.id_evento=e.id_evento
               LEFT JOIN contratos c ON p.id_contrato=c.id_contrato
               ORDER BY p.id_pago DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            """SELECT p.id_pago, COALESCE(c.nro_contrato,'—'), p.tipo_pago,
                      p.monto, p.fecha_pago, p.estado
               FROM pagos p LEFT JOIN contratos c ON p.id_contrato=c.id_contrato
               WHERE p.id_evento=%s ORDER BY p.id_pago""",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_pago):
    try:
        return execute_query_one(
            "SELECT id_pago, id_evento, id_contrato, tipo_pago, monto, fecha_pago, estado FROM pagos WHERE id_pago=%s",
            (id_pago,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def create(id_evento, id_contrato, tipo_pago, monto, fecha_pago):
    try:
        execute_insert(
            "INSERT INTO pagos (id_evento, id_contrato, tipo_pago, monto, fecha_pago) VALUES (%s,%s,%s,%s,%s)",
            (id_evento, id_contrato if id_contrato else None, tipo_pago, monto, fecha_pago)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error al registrar pago: {e}")
        return False

def cambiar_estado(id_pago, nuevo_estado):
    try:
        execute_insert("UPDATE pagos SET estado=%s WHERE id_pago=%s", (nuevo_estado, id_pago))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_pago, monto, fecha_pago, estado):
    try:
        execute_insert("UPDATE pagos SET monto=%s, fecha_pago=%s, estado=%s WHERE id_pago=%s",
                       (monto, fecha_pago, estado, id_pago))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_pago):
    return cambiar_estado(id_pago, 'Anulado')
