"""
Página exclusiva para la Secretaria de Eventos.
Cubre todo CU1 + requerimientos:
  - Listado y registro de clientes
  - Creación de eventos y asignación a cliente
  - Registro de requerimientos del evento
  - Gestión de contratos (crear, ver estado)
"""
import streamlit as st
import pandas as pd
from datetime import date
from auth.roles import requiere_rol
from cu1_contratos import model_cliente, model_contrato
from cu2_planificacion import model_evento
from cu2_planificacion.model_requerimiento import (
    get_by_evento, create as create_req, delete as delete_req, TIPOS_RECURSO
)
from cu3_recursos import model_proveedor
from shared.utils import validate_email, format_currency, generar_nro_contrato, paginate_dataframe

TIPOS_CLIENTE = ["Persona Natural", "Empresa", "Institución"]
TIPOS_EVENTO  = ["Corporativo", "Social", "Institucional", "Cultural", "Deportivo", "Otro"]


def show():
    requiere_rol(['Secretaria de Eventos', 'Administrador'])
    st.title("🗂️ Gestión de Clientes, Eventos y Contratos")

    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Clientes",
        "📅 Eventos",
        "📦 Requerimientos",
        "📄 Contratos",
    ])

    # ──────────────────────────────────────────────────────────
    # TAB 1 — CLIENTES
    # ──────────────────────────────────────────────────────────
    with tab1:
        st.subheader("🔍 Buscar Clientes")
        busqueda = st.text_input("Buscar por nombre o email", key="cli_busqueda")
        if busqueda:
            rows = model_cliente.search(busqueda)
            cols = ["ID", "Nombre", "Tipo", "Email", "Teléfono", "Estado"]
        else:
            rows = model_cliente.get_all()
            cols = ["ID", "Nombre", "Tipo", "Dirección", "Email", "Teléfono", "Fecha Reg.", "Estado"]

        if rows:
            df = pd.DataFrame(rows, columns=cols)
            df_page, _, _ = paginate_dataframe(df)
            st.dataframe(df_page, use_container_width=True)
        else:
            st.info("No se encontraron clientes.")

        st.divider()
        st.subheader("➕ Registrar Nuevo Cliente")
        with st.form("form_nuevo_cliente_sec"):
            c1, c2 = st.columns(2)
            nombre_c       = c1.text_input("Nombre *")
            tipo_cliente_c = c2.selectbox("Tipo de cliente *", TIPOS_CLIENTE)
            email_c        = c1.text_input("Email *")
            telefono_c     = c2.text_input("Teléfono")
            direccion_c    = st.text_area("Dirección")
            if st.form_submit_button("Registrar Cliente"):
                if not nombre_c or not email_c:
                    st.error("Nombre y email son obligatorios.")
                elif not validate_email(email_c):
                    st.error("Formato de email inválido.")
                else:
                    if model_cliente.create(nombre_c, tipo_cliente_c, direccion_c, email_c, telefono_c):
                        st.success(f"✅ Cliente '{nombre_c}' registrado exitosamente.")
                        st.rerun()

        st.divider()
        st.subheader("🔄 Cambiar Estado de Cliente")
        id_cli_estado = st.number_input("ID del cliente", min_value=1, step=1, key="cli_estado_id")
        if st.button("Activar / Inactivar Cliente"):
            if model_cliente.toggle_estado(int(id_cli_estado)):
                st.success("Estado del cliente actualizado.")
                st.rerun()

    # ──────────────────────────────────────────────────────────
    # TAB 2 — EVENTOS
    # ──────────────────────────────────────────────────────────
    with tab2:
        st.subheader("📋 Listado de Eventos")
        rows_ev = model_evento.get_all()
        if rows_ev:
            df_ev = pd.DataFrame(
                rows_ev,
                columns=["ID", "Nombre", "Tipo", "Lugar", "Fecha", "Monto", "Estado", "Cliente"]
            )
            st.dataframe(df_ev, use_container_width=True)
        else:
            st.info("Aún no hay eventos registrados.")

        st.divider()
        st.subheader("➕ Registrar Nuevo Evento")
        clientes_activos = model_cliente.get_activos()
        if not clientes_activos:
            st.warning("⚠️ No hay clientes activos. Registra un cliente primero.")
        else:
            cli_op = {f"{c[1]} (ID:{c[0]})": c[0] for c in clientes_activos}
            with st.form("form_nuevo_evento_sec"):
                c1, c2 = st.columns(2)
                nombre_ev   = c1.text_input("Nombre del evento *")
                tipo_ev     = c2.selectbox("Tipo de evento", TIPOS_EVENTO)
                lugar_ev    = c1.text_input("Lugar")
                fecha_ev    = c2.date_input("Fecha del evento")
                monto_ev    = st.number_input("Monto estimado S/", min_value=0.0, step=100.0)
                cliente_sel = st.selectbox("Cliente *", list(cli_op.keys()))
                if st.form_submit_button("Registrar Evento"):
                    if not nombre_ev:
                        st.error("El nombre del evento es obligatorio.")
                    else:
                        id_cli = cli_op[cliente_sel]
                        if model_evento.create(nombre_ev, tipo_ev, lugar_ev, fecha_ev, monto_ev, id_cli):
                            st.success(f"✅ Evento '{nombre_ev}' registrado exitosamente.")
                            st.rerun()

    # ──────────────────────────────────────────────────────────
    # TAB 3 — REQUERIMIENTOS
    # ──────────────────────────────────────────────────────────
    with tab3:
        st.subheader("📦 Requerimientos del Evento")
        eventos_act = model_evento.get_activos()
        if not eventos_act:
            st.warning("No hay eventos activos.")
        else:
            ev_op_r = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_act}
            ev_sel_r = st.selectbox("Seleccionar Evento", list(ev_op_r.keys()), key="req_ev_sec")
            id_ev_r  = ev_op_r[ev_sel_r]

            reqs = get_by_evento(id_ev_r)
            if reqs:
                df_req = pd.DataFrame(reqs, columns=["ID", "Descripción", "Tipo Recurso", "Cantidad"])
                st.dataframe(df_req, use_container_width=True)

                st.subheader("🗑️ Eliminar Requerimiento")
                id_req_del = st.number_input("ID del requerimiento a eliminar", min_value=1, step=1)
                if st.button("Eliminar Requerimiento"):
                    if delete_req(int(id_req_del)):
                        st.success("Requerimiento eliminado.")
                        st.rerun()
            else:
                st.info("Este evento aún no tiene requerimientos registrados.")

            st.divider()
            st.subheader("➕ Agregar Requerimiento")
            with st.form("form_nuevo_req_sec"):
                desc_r = st.text_input("Descripción *")
                tipo_r = st.selectbox("Tipo de recurso", TIPOS_RECURSO)
                cant_r = st.number_input("Cantidad", min_value=1, step=1, value=1)
                if st.form_submit_button("Agregar Requerimiento"):
                    if not desc_r:
                        st.error("La descripción es obligatoria.")
                    elif create_req(id_ev_r, desc_r, tipo_r, cant_r):
                        st.success("✅ Requerimiento agregado.")
                        st.rerun()

    # ──────────────────────────────────────────────────────────
    # TAB 4 — CONTRATOS
    # ──────────────────────────────────────────────────────────
    with tab4:
        st.subheader("📋 Contratos Registrados")
        rows_ct = model_contrato.get_all()
        if rows_ct:
            df_ct = pd.DataFrame(
                rows_ct,
                columns=["ID", "Nro. Contrato", "Evento", "Proveedor", "Fecha", "Estado", "Monto", "Firma Digital"]
            )
            df_ct["Monto"] = df_ct["Monto"].apply(format_currency)
            st.dataframe(df_ct, use_container_width=True)
        else:
            st.info("No hay contratos registrados.")

        st.divider()
        st.subheader("➕ Generar Nuevo Contrato")
        eventos_ct  = model_evento.get_activos()
        proveedores = model_proveedor.get_all()

        if not eventos_ct:
            st.warning("⚠️ No hay eventos activos para asociar un contrato.")
        elif not proveedores:
            st.warning("⚠️ No hay proveedores registrados. Pide al Jefe de Logística que los registre.")
        else:
            ev_op_ct   = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_ct}
            prov_op_ct = {f"{p[1]} — {p[2]} (ID:{p[0]})": p[0] for p in proveedores}

            with st.form("form_nuevo_contrato_sec"):
                ev_sel_ct   = st.selectbox("Evento *", list(ev_op_ct.keys()))
                prov_sel_ct = st.selectbox("Proveedor *", list(prov_op_ct.keys()))

                id_ev_ct   = ev_op_ct[ev_sel_ct]
                id_prov_ct = prov_op_ct[prov_sel_ct]

                # Auto-completar datos del cliente
                ev_data = model_evento.get_by_id(id_ev_ct)
                if ev_data and len(ev_data) > 7:
                    cliente = model_cliente.get_by_id(ev_data[7])
                    if cliente:
                        st.info(f"🧑 Cliente asociado: **{cliente[1]}** | 📧 {cliente[4]}")

                c1, c2 = st.columns(2)
                fecha_ct  = c1.date_input("Fecha del contrato", value=date.today())
                monto_ct  = c2.number_input("Monto S/ *", min_value=0.0, step=100.0)
                desc_ct   = st.text_area("Descripción del contrato")
                firma_ct  = st.checkbox("Firma digital confirmada")

                corr = model_contrato.get_next_correlativo()
                nro  = generar_nro_contrato(corr)
                st.info(f"📝 Nro. de contrato generado: **{nro}**")

                if st.form_submit_button("Generar Contrato"):
                    if monto_ct <= 0:
                        st.error("El monto debe ser mayor a 0.")
                    else:
                        if model_contrato.create(nro, id_ev_ct, id_prov_ct, fecha_ct, monto_ct, desc_ct, firma_ct):
                            st.success(f"✅ Contrato **{nro}** generado exitosamente. Pendiente de aprobación por el Jefe de Eventos.")
                            st.rerun()
