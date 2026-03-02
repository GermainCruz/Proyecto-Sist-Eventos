import psycopg2
import streamlit as st
from database.connection import execute_query, execute_query_one, execute_insert

DIMENSIONES = ["Calidad del servicio", "Cumplimiento del programa", "Recursos disponibles", "Comunicación previa"]

def get_all():
    try:
        return execute_query(
            """SELECT enc.id_encuesta, e.nombre AS evento, enc.fecha_evaluacion,
                      enc.nivel_satisfaccion, enc.estado_evaluacion, enc.comentarios
               FROM encuestas enc JOIN eventos e ON enc.id_evento=e.id_evento
               ORDER BY enc.id_encuesta DESC"""
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_evento(id_evento):
    try:
        return execute_query(
            "SELECT id_encuesta, fecha_evaluacion, nivel_satisfaccion, estado_evaluacion, comentarios FROM encuestas WHERE id_evento=%s ORDER BY id_encuesta",
            (id_evento,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def get_by_id(id_enc):
    try:
        return execute_query_one(
            "SELECT id_encuesta, id_evento, fecha_evaluacion, nivel_satisfaccion, estado_evaluacion, comentarios FROM encuestas WHERE id_encuesta=%s",
            (id_enc,)
        )
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return None

def get_detalles(id_encuesta):
    try:
        return execute_query(
            "SELECT id_detalle_encuesta, pregunta, respuesta FROM detalle_encuesta WHERE id_encuesta=%s ORDER BY id_detalle_encuesta",
            (id_encuesta,)
        ) or []
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return []

def create(id_evento, fecha_evaluacion, nivel_satisfaccion, comentarios):
    try:
        row = execute_insert(
            """INSERT INTO encuestas (id_evento, fecha_evaluacion, nivel_satisfaccion, comentarios)
               VALUES (%s,%s,%s,%s) RETURNING id_encuesta""",
            (id_evento, fecha_evaluacion, nivel_satisfaccion, comentarios)
        )
        return row[0] if row else None
    except psycopg2.Error as e:
        st.error(f"Error al crear encuesta: {e}")
        return None

def create_detalle(id_encuesta, pregunta, respuesta):
    try:
        execute_insert(
            "INSERT INTO detalle_encuesta (id_encuesta, pregunta, respuesta) VALUES (%s,%s,%s)",
            (id_encuesta, pregunta, respuesta)
        )
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def completar_encuesta(id_encuesta):
    try:
        execute_insert("UPDATE encuestas SET estado_evaluacion='Completada' WHERE id_encuesta=%s", (id_encuesta,))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def update(id_enc, comentarios, nivel_satisfaccion):
    try:
        execute_insert("UPDATE encuestas SET comentarios=%s, nivel_satisfaccion=%s WHERE id_encuesta=%s",
                       (comentarios, nivel_satisfaccion, id_enc))
        return True
    except psycopg2.Error as e:
        st.error(f"Error: {e}")
        return False

def delete(id_enc):
    st.warning("Las encuestas no se eliminan.")
    return False
