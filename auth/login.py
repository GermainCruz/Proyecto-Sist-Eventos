import streamlit as st
import bcrypt
import logging
from database.connection import execute_query_one

logger = logging.getLogger(__name__)

def show_login():
    st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem;'>
            <h1>🎪 Sistema de Gestión de Eventos</h1>
            <p style='color: gray;'>Inicia sesión para continuar</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            st.subheader("Iniciar Sesión")
            user_login = st.text_input("Usuario", placeholder="Tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)

        if submitted:
            if not user_login or not password:
                st.error("Ingresa usuario y contraseña.")
                return

            try:
                row = execute_query_one(
                    """SELECT id_usuario, nombre, apellido, email, user_login,
                              password_hash, rol, estado
                       FROM usuarios WHERE user_login = %s""",
                    (user_login,)
                )
                if row is None:
                    st.error("Usuario o contraseña incorrectos.")
                    return

                (id_u, nombre, apellido, email, u_login,
                 password_hash, rol, estado) = row

                if estado != 'Activo':
                    st.error("Tu cuenta está inactiva. Contacta al administrador.")
                    return

                if bcrypt.checkpw(password.encode(), password_hash.encode()):
                    st.session_state.autenticado = True
                    st.session_state.id_usuario  = id_u
                    st.session_state.nombre      = nombre
                    st.session_state.apellido    = apellido
                    st.session_state.email       = email
                    st.session_state.user_login  = u_login
                    st.session_state.rol         = rol
                    st.success(f"¡Bienvenido, {nombre}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

            except Exception as e:
                logger.error(f"Error en login: {e}")
                st.error("Error de conexión. Contacta al administrador.")
