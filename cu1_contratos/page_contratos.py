import streamlit as st
import pandas as pd
from datetime import date
from auth.roles import requiere_rol
from cu1_contratos import model_contrato, model_cliente
from cu3_recursos import model_proveedor
from cu2_planificacion import model_evento
from shared.utils import format_currency, generar_nro_contrato

def show():
    requiere_rol(['Administrador', 'Jefe de Eventos'])
    st.title("📄 Gestión de Contratos")
    tab1, tab2 = st.tabs(["📋 Contratos Existentes", "➕ Nuevo Contrato"])

    # ── Contratos existentes ──────────────────────────────────
    with tab1:
        rows = model_contrato.get_all()
        if rows:
            df = pd.DataFrame(rows, columns=["ID","Nro. Contrato","Evento","Proveedor","Fecha","Estado","Monto","Firma Digital"])
            df["Monto"] = df["Monto"].apply(lambda x: format_currency(x))
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay contratos registrados.")

        st.divider()
        st.subheader("Gestionar Contrato")
        id_contrato = st.number_input("ID del Contrato", min_value=1, step=1)
        contrato = model_contrato.get_by_id(int(id_contrato))

        if contrato:
            (cid, nro, id_ev, id_prov, fecha, estado, monto, desc, firma) = contrato
            st.info(f"**Contrato:** {nro} | **Estado:** {estado} | **Monto:** {format_currency(monto)}")

            c1, c2, c3, c4 = st.columns(4)
            if estado == 'Pendiente':
                if c1.button("✅ Aprobar"):
                    if model_contrato.cambiar_estado(cid, 'Aprobado'):
                        st.success("Contrato aprobado.")
                        st.rerun()
                if c2.button("❌ Rechazar"):
                    if model_contrato.cambiar_estado(cid, 'Rechazado'):
                        st.warning("Contrato rechazado.")
                        st.rerun()
                with st.expander("✏️ Modificar Contrato"):
                    with st.form("form_mod_contrato"):
                        nuevo_monto = st.number_input("Monto", value=float(monto or 0), min_value=0.0)
                        nueva_desc  = st.text_area("Descripción", value=desc or "")
                        nueva_fecha = st.date_input("Fecha", value=fecha)
                        nueva_firma = st.checkbox("Firma digital", value=firma)
                        if st.form_submit_button("Guardar Cambios"):
                            model_contrato.update(cid, nuevo_monto, nueva_desc, nueva_fecha, nueva_firma)
                            st.success("Contrato modificado.")
                            st.rerun()

            if estado in ('Aprobado','Firmado'):
                if c3.button("🤝 Confirmar Cumplimiento"):
                    model_contrato.confirmar_cumplimiento(cid)
                    st.success("Contrato marcado como Cumplido.")
                    st.rerun()
        else:
            st.caption("Ingresa un ID válido para gestionar el contrato.")

    # ── Nuevo contrato ────────────────────────────────────────
    with tab2:
        eventos  = model_evento.get_activos()
        proveedores = model_proveedor.get_all()

        if not eventos:
            st.warning("No hay eventos activos.")
            return
        if not proveedores:
            st.warning("No hay proveedores registrados.")
            return

        ev_opciones = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos}
        prov_opciones = {f"{p[1]} - {p[2]} (ID:{p[0]})": p[0] for p in proveedores}

        with st.form("form_nuevo_contrato"):
            st.subheader("Generar Nuevo Contrato")
            ev_sel   = st.selectbox("Evento *", list(ev_opciones.keys()))
            prov_sel = st.selectbox("Proveedor *", list(prov_opciones.keys()))

            id_ev_sel   = ev_opciones[ev_sel]
            id_prov_sel = prov_opciones[prov_sel]

            # Obtener info del cliente para autocompletar
            ev_data = model_evento.get_by_id(id_ev_sel)
            if ev_data:
                cliente = model_cliente.get_by_id(ev_data[7]) if len(ev_data) > 7 else None
                if cliente:
                    st.info(f"Cliente: {cliente[1]} | Email: {cliente[4]}")

            c1, c2 = st.columns(2)
            fecha_contrato = c1.date_input("Fecha del contrato *", value=date.today())
            monto          = c2.number_input("Monto *", min_value=0.0, step=100.0)
            descripcion    = st.text_area("Descripción del contrato")
            firma_digital  = st.checkbox("Firma digital confirmada")

            corr = model_contrato.get_next_correlativo()
            nro  = generar_nro_contrato(corr)
            st.info(f"Nro. de contrato generado: **{nro}**")

            if st.form_submit_button("Generar Contrato"):
                if monto <= 0:
                    st.error("El monto debe ser mayor a 0.")
                else:
                    if model_contrato.create(nro, id_ev_sel, id_prov_sel, fecha_contrato, monto, descripcion, firma_digital):
                        st.success(f"Contrato **{nro}** creado exitosamente.")
                        st.rerun()
