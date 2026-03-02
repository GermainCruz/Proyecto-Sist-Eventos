import streamlit as st
import pandas as pd
from auth.roles import requiere_rol
from shared import model_usuario
from config import ROLES
from shared.utils import validate_email

def show():
    requiere_rol(['Administrador'])
    st.title("👤 Gestión de Usuarios")
    tab1, tab2 = st.tabs(["📋 Usuarios", "➕ Nuevo Usuario"])

    with tab1:
        rows = model_usuario.get_all()
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Nombre", "Apellido", "Email", "Usuario", "Rol", "Estado", "Creado"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay usuarios registrados.")

        st.subheader("Editar Usuario")
        usuarios = model_usuario.get_all()
        opciones = {f"{r[1]} {r[2]} ({r[4]}) - {r[5]}": r[0] for r in usuarios}
        sel = st.selectbox("Seleccionar usuario", list(opciones.keys()))
        if sel:
            uid = opciones[sel]
            u = model_usuario.get_by_id(uid)
            if u:
                with st.form("form_edit_user"):
                    c1, c2 = st.columns(2)
                    nombre   = c1.text_input("Nombre",   value=u[1])
                    apellido = c2.text_input("Apellido", value=u[2])
                    email    = c1.text_input("Email",    value=u[3])
                    rol      = c2.selectbox("Rol", ROLES, index=ROLES.index(u[5]))
                    estado   = st.selectbox("Estado", ["Activo", "Inactivo"], index=0 if u[6] == "Activo" else 1)
                    nueva_pass = st.text_input("Nueva contraseña (dejar vacío para no cambiar)", type="password")
                    if st.form_submit_button("Guardar Cambios"):
                        if not validate_email(email):
                            st.error("Email inválido.")
                        else:
                            if model_usuario.update(uid, nombre, apellido, email, rol, estado):
                                if nueva_pass:
                                    model_usuario.update_password(uid, nueva_pass)
                                st.success("Usuario actualizado correctamente.")
                                st.rerun()

    with tab2:
        with st.form("form_nuevo_user"):
            st.subheader("Crear Nuevo Usuario")
            c1, c2 = st.columns(2)
            nombre     = c1.text_input("Nombre")
            apellido   = c2.text_input("Apellido")
            email      = c1.text_input("Email")
            user_login = c2.text_input("Usuario (login)")
            rol        = st.selectbox("Rol", ROLES)
            password   = st.text_input("Contraseña", type="password")
            confirm    = st.text_input("Confirmar contraseña", type="password")
            if st.form_submit_button("Crear Usuario"):
                if not all([nombre, apellido, email, user_login, password]):
                    st.error("Todos los campos son obligatorios.")
                elif not validate_email(email):
                    st.error("Email inválido.")
                elif password != confirm:
                    st.error("Las contraseñas no coinciden.")
                else:
                    if model_usuario.create(nombre, apellido, email, user_login, password, rol):
                        st.success(f"Usuario '{user_login}' creado exitosamente.")
                        st.rerun()
