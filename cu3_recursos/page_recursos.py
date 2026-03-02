import streamlit as st
import pandas as pd
from datetime import date
from auth.roles import requiere_rol
from cu3_recursos import model_proveedor, model_recurso, model_asignacion, model_orden_compra
from cu2_planificacion import model_evento
from shared.utils import format_currency

def show():
    requiere_rol(['Administrador', 'Jefe de Logística'])
    st.title("📦 Gestión de Recursos y Proveedores")
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Proveedores", "📦 Recursos", "🔗 Asignaciones", "🛒 Órdenes de Compra"])

    # ── TAB 1: Proveedores ────────────────────────────────────
    with tab1:
        rows_p = model_proveedor.get_all()
        if rows_p:
            df_p = pd.DataFrame(rows_p, columns=["ID","Nombre","Tipo Servicio","Disponible","Email","Teléfono"])
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("No hay proveedores.")

        col_a, col_b = st.columns(2)
        with col_a:
            with st.form("form_nuevo_prov"):
                st.subheader("Nuevo Proveedor")
                nombre_p = st.text_input("Nombre *")
                tipo_s   = st.text_input("Tipo de servicio *")
                disp     = st.checkbox("Disponible", value=True)
                email_p  = st.text_input("Email")
                tel_p    = st.text_input("Teléfono")
                if st.form_submit_button("Registrar"):
                    if not nombre_p or not tipo_s:
                        st.error("Nombre y tipo de servicio son obligatorios.")
                    elif model_proveedor.create(nombre_p, tipo_s, disp, email_p, tel_p):
                        st.success("Proveedor registrado.")
                        st.rerun()

        with col_b:
            with st.form("form_edit_prov"):
                st.subheader("Editar Proveedor")
                id_prov = st.number_input("ID del proveedor", min_value=1, step=1)
                prov = model_proveedor.get_by_id(int(id_prov))
                if prov:
                    n_nombre = st.text_input("Nombre", value=prov[1])
                    n_tipo   = st.text_input("Tipo servicio", value=prov[2])
                    n_disp   = st.checkbox("Disponible", value=bool(prov[3]))
                    n_email  = st.text_input("Email", value=prov[4] or "")
                    n_tel    = st.text_input("Teléfono", value=prov[5] or "")
                    if st.form_submit_button("Guardar"):
                        model_proveedor.update(id_prov, n_nombre, n_tipo, n_disp, n_email, n_tel)
                        st.success("Proveedor actualizado.")
                        st.rerun()

    # ── TAB 2: Recursos ───────────────────────────────────────
    with tab2:
        rows_r = model_recurso.get_all()
        if rows_r:
            df_r = pd.DataFrame(rows_r, columns=["ID","Nombre","Tipo","Cantidad","Estado","Proveedor"])
            st.dataframe(df_r, use_container_width=True)

        col_a, col_b = st.columns(2)
        proveedores = model_proveedor.get_all()
        prov_op = {"— Sin proveedor —": None}
        prov_op.update({f"{p[1]} (ID:{p[0]})": p[0] for p in proveedores})

        with col_a:
            with st.form("form_nuevo_rec"):
                st.subheader("Nuevo Recurso")
                nombre_r  = st.text_input("Nombre *")
                tipo_r    = st.selectbox("Tipo", model_recurso.TIPOS_RECURSO)
                cantidad  = st.number_input("Cantidad", min_value=0, step=1)
                estado_r  = st.selectbox("Estado", model_recurso.ESTADOS_RECURSO)
                prov_sel  = st.selectbox("Proveedor", list(prov_op.keys()))
                if st.form_submit_button("Registrar"):
                    if not nombre_r:
                        st.error("El nombre es obligatorio.")
                    else:
                        id_p = prov_op[prov_sel]
                        if model_recurso.create(nombre_r, tipo_r, cantidad, estado_r, id_p):
                            st.success("Recurso registrado.")
                            st.rerun()

        with col_b:
            with st.form("form_estado_rec"):
                st.subheader("Cambiar Estado de Recurso")
                id_rec  = st.number_input("ID del recurso", min_value=1, step=1)
                n_est_r = st.selectbox("Nuevo estado", model_recurso.ESTADOS_RECURSO)
                if st.form_submit_button("Actualizar Estado"):
                    model_recurso.cambiar_estado(int(id_rec), n_est_r)
                    st.success("Estado actualizado.")
                    st.rerun()

    # ── TAB 3: Asignaciones ───────────────────────────────────
    with tab3:
        rows_a = model_asignacion.get_all()
        if rows_a:
            df_a = pd.DataFrame(rows_a, columns=["ID","Evento","Recurso","Cantidad","Fecha Asig.","Estado"])
            st.dataframe(df_a, use_container_width=True)

        eventos_act = model_evento.get_activos()
        recursos_disp = [r for r in model_recurso.get_all() if r[4] == 'Disponible']

        if eventos_act and recursos_disp:
            ev_op_a  = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_act}
            rec_op_a = {f"{r[1]} - Cant:{r[3]} (ID:{r[0]})": r[0] for r in recursos_disp}

            with st.form("form_asignacion"):
                st.subheader("Nueva Asignación")
                ev_sel_a  = st.selectbox("Evento", list(ev_op_a.keys()))
                rec_sel_a = st.selectbox("Recurso disponible", list(rec_op_a.keys()))
                cant_a    = st.number_input("Cantidad a asignar", min_value=1, step=1)
                fecha_a   = st.date_input("Fecha de asignación", value=date.today())
                if st.form_submit_button("Confirmar Asignación"):
                    id_ev_a  = ev_op_a[ev_sel_a]
                    id_rec_a = rec_op_a[rec_sel_a]
                    if model_asignacion.create(id_ev_a, id_rec_a, cant_a, fecha_a):
                        model_recurso.cambiar_estado(id_rec_a, 'Asignado')
                        st.success("Asignación confirmada y recurso marcado como Asignado.")
                        st.rerun()

    # ── TAB 4: Órdenes de Compra ──────────────────────────────
    with tab4:
        rows_oc = model_orden_compra.get_all()
        if rows_oc:
            df_oc = pd.DataFrame(rows_oc, columns=["ID","Evento","Proveedor","Recurso","Fecha","Estado","Monto"])
            df_oc["Monto"] = df_oc["Monto"].apply(format_currency)
            st.dataframe(df_oc, use_container_width=True)

        st.subheader("Gestionar Orden de Compra")
        id_oc = st.number_input("ID de la OC", min_value=1, step=1)
        oc = model_orden_compra.get_by_id(int(id_oc))
        if oc:
            (oc_id, oc_ev, oc_prov, oc_rec, oc_cot, oc_fecha, oc_est, oc_monto) = oc
            st.info(f"Estado: **{oc_est}** | Monto: {format_currency(oc_monto)}")
            col1, col2, col3, col4 = st.columns(4)
            if oc_est == 'Pendiente':
                if col1.button("🔍 Enviar a Revisión"):
                    model_orden_compra.cambiar_estado(oc_id, 'En Revisión')
                    st.rerun()
            if oc_est == 'En Revisión':
                if col2.button("✅ Aprobar OC"):
                    model_orden_compra.cambiar_estado(oc_id, 'Aprobada')
                    st.success("OC Aprobada. Se notificará al proveedor.")
                    st.rerun()
                if col3.button("❌ Rechazar OC"):
                    model_orden_compra.cambiar_estado(oc_id, 'Rechazada')
                    st.warning("OC Rechazada.")
                    st.rerun()
            if oc_est == 'Aprobada':
                if col4.button("📤 Enviar al Proveedor"):
                    model_orden_compra.cambiar_estado(oc_id, 'Enviada')
                    st.success("OC enviada al proveedor.")
                    st.rerun()
            if oc_est == 'Enviada':
                if st.button("📥 Confirmar Recepción"):
                    model_orden_compra.cambiar_estado(oc_id, 'Recibida')
                    st.success("Recepción confirmada.")
                    st.rerun()

        st.divider()
        eventos_oc = model_evento.get_activos()
        proveedores_oc = model_proveedor.get_all()
        recursos_oc = model_recurso.get_all()
        if eventos_oc and proveedores_oc and recursos_oc:
            ev_op_oc  = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_oc}
            prov_op_oc = {f"{p[1]} (ID:{p[0]})": p[0] for p in proveedores_oc}
            rec_op_oc  = {f"{r[1]} (ID:{r[0]})": r[0] for r in recursos_oc}
            with st.form("form_nueva_oc"):
                st.subheader("Nueva Orden de Compra")
                ev_sel_oc   = st.selectbox("Evento", list(ev_op_oc.keys()))
                prov_sel_oc = st.selectbox("Proveedor", list(prov_op_oc.keys()))
                rec_sel_oc  = st.selectbox("Recurso", list(rec_op_oc.keys()))
                fecha_oc    = st.date_input("Fecha", value=date.today())
                monto_oc    = st.number_input("Monto S/", min_value=0.0)
                cot_ref     = st.number_input("ID Cotización (opcional, 0=sin cotización)", min_value=0, step=1)
                if st.form_submit_button("Crear Orden de Compra"):
                    id_cot_ref = int(cot_ref) if cot_ref > 0 else None
                    if model_orden_compra.create(
                        ev_op_oc[ev_sel_oc], prov_op_oc[prov_sel_oc],
                        rec_op_oc[rec_sel_oc], id_cot_ref, fecha_oc, monto_oc
                    ):
                        st.success("Orden de Compra creada.")
                        st.rerun()
