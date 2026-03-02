import streamlit as st
from functools import wraps

def requiere_rol(roles_permitidos: list):
    """Verifica que el usuario tenga uno de los roles permitidos."""
    rol_actual = st.session_state.get("rol", "")
    if rol_actual not in roles_permitidos:
        st.warning(f"⛔ Acceso denegado. Esta sección requiere uno de los siguientes roles: {', '.join(roles_permitidos)}")
        st.stop()

def check_rol(roles_permitidos: list) -> bool:
    """Retorna True si el usuario tiene el rol requerido."""
    return st.session_state.get("rol", "") in roles_permitidos
