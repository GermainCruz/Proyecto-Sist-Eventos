import streamlit as st
import pandas as pd
from auth.roles import requiere_rol
from cu1_contratos import model_cliente
from shared.utils import validate_email, paginate_dataframe

TIPOS_CLIENTE = ["Persona Natural", "Empresa", "Institución"]

def show():
    requiere_rol(['Administrador', 'Secretaria de Eventos', 'Jefe de Eventos'])
    st.title("👥 Gestión de Clientes")
    tab1, tab2 = st.tabs(["📋 Listado y Búsqueda", "➕ Nuevo Cliente"])

    # ── Listado y búsqueda ────────────────────────────────────
    with tab1:
        busqueda = st.text_input("🔍 Buscar por nombre o email", "")
        if busqueda:
            rows = model_cliente.search(busqueda)
        else:
            rows = model_cliente.get_all()

        if rows:
            cols = ["ID", "Nombre", "Tipo", "Email", "Teléfono", "Estado"] if busqueda else \
                   ["ID", "Nombre", "Tipo", "Dirección", "Email", "Teléfono", "Fecha Reg.", "Estado"]
            df = pd.DataFrame(rows, columns=cols)
            df_page, _, _ = paginate_dataframe(df)
            st.dataframe(df_page, use_container_width=True)

            st.subheader("Cambiar Estado")
            id_sel = st.number_input("ID del cliente", min_value=1, step=1)
            if st.button("Activar / Inactivar"):
                if model_cliente.toggle_estado(int(id_sel)):
                    st.success("Estado actualizado.")
                    st.rerun()
        else:
            st.info("No se encontraron clientes.")

    # ── Nuevo cliente ─────────────────────────────────────────
    with tab2:
        with st.form("form_nuevo_cliente"):
            st.subheader("Registrar Nuevo Cliente")
            c1, c2 = st.columns(2)
            nombre       = c1.text_input("Nombre *")
            tipo_cliente = c2.selectbox("Tipo de cliente *", TIPOS_CLIENTE)
            email        = c1.text_input("Email *")
            telefono     = c2.text_input("Teléfono")
            direccion    = st.text_area("Dirección")
            submitted    = st.form_submit_button("Registrar Cliente")

        if submitted:
            if not nombre or not email:
                st.error("Nombre y email son obligatorios.")
            elif not validate_email(email):
                st.error("Email inválido.")
            else:
                if model_cliente.create(nombre, tipo_cliente, direccion, email, telefono):
                    st.success(f"Cliente '{nombre}' registrado exitosamente.")
                    st.rerun()
