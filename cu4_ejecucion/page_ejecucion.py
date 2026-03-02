import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from fpdf import FPDF
import io
from auth.roles import requiere_rol, check_rol
from cu4_ejecucion import model_incidencia, model_pago, model_encuesta
from cu2_planificacion import model_evento
from cu1_contratos import model_contrato
from cu3_recursos import model_asignacion, model_recurso
from shared.utils import format_currency

def show():
    requiere_rol(['Administrador', 'Jefe de Eventos', 'Jefe de Logística', 'Secretaria de Eventos'])
    st.title("🚀 Gestión de Ejecución y Cierre de Eventos")
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ Ejecución", "🔥 Incidencias", "💳 Pagos", "⭐ Encuestas"])

    eventos_act = model_evento.get_activos()
    if not eventos_act:
        st.warning("No hay eventos activos.")
        return

    ev_opciones = {f"{e[1]} [{e[2]}] (ID:{e[0]})": e[0] for e in eventos_act}

    # ── TAB 1: Ejecución ──────────────────────────────────────
    with tab1:
        ev_sel = st.selectbox("Seleccionar Evento", list(ev_opciones.keys()), key="exec_ev")
        id_ev  = ev_opciones[ev_sel]
        ev_data = model_evento.get_by_id(id_ev)
        estado_ev = ev_data[6] if ev_data else "—"

        col1, col2 = st.columns(2)
        col1.metric("Estado actual", estado_ev)

        if estado_ev != 'Confirmada':
            st.warning(f"⚠️ El evento no está Confirmado (estado: {estado_ev}). Confirma la planificación antes de iniciar ejecución.")
        else:
            if col2.button("▶️ Iniciar Ejecución"):
                if model_evento.cambiar_estado(id_ev, 'En Ejecución'):
                    st.success("Evento en ejecución.")
                    st.rerun()

        # Recursos del evento
        st.subheader("Recursos asignados al evento")
        asignaciones = model_asignacion.get_by_evento(id_ev)
        if asignaciones:
            df_as = pd.DataFrame(asignaciones, columns=["ID Asig.","Recurso","Cantidad","Fecha Asig.","Estado"])
            st.dataframe(df_as, use_container_width=True)
        else:
            st.warning("⚠️ No hay recursos asignados. Verificar en módulo de Logística.")

        # Contratos del evento
        st.subheader("Contratos del evento")
        contratos = model_contrato.get_by_evento(id_ev)
        if contratos:
            df_ct = pd.DataFrame(contratos, columns=["ID","Nro. Contrato","Estado","Monto","Firma Digital"])
            st.dataframe(df_ct, use_container_width=True)

        st.divider()
        if check_rol(['Administrador','Jefe de Eventos']):
            col_a, col_b = st.columns(2)
            if estado_ev == 'En Ejecución':
                if col_a.button("🔒 Cerrar Evento Formalmente"):
                    model_evento.cambiar_estado(id_ev, 'Cerrada')
                    st.success("Evento cerrado formalmente.")
                    st.rerun()
            if contratos:
                id_ct = st.number_input("ID contrato para confirmar cumplimiento", min_value=1, step=1)
                if st.button("✅ Confirmar Cumplimiento del Contrato"):
                    model_contrato.confirmar_cumplimiento(int(id_ct))
                    st.success("Cumplimiento del contrato confirmado.")
                    st.rerun()

    # ── TAB 2: Incidencias ────────────────────────────────────
    with tab2:
        ev_sel2 = st.selectbox("Evento", list(ev_opciones.keys()), key="inc_ev")
        id_ev2  = ev_opciones[ev_sel2]

        incidencias = model_incidencia.get_by_evento(id_ev2)
        if incidencias:
            df_inc = pd.DataFrame(incidencias, columns=["ID","Tipo","Descripción","Fecha","Estado"])
            st.dataframe(df_inc, use_container_width=True)

            id_inc = st.number_input("ID incidencia para ver detalle / cambiar estado", min_value=1, step=1)
            inc = model_incidencia.get_by_id(int(id_inc))
            if inc:
                detalles = model_incidencia.get_detalles(id_inc)
                if detalles:
                    df_det = pd.DataFrame(detalles, columns=["ID Det.","Descripción","Acción Tomada","Fecha"])
                    st.dataframe(df_det, use_container_width=True)

                col_x, col_y = st.columns(2)
                estados_inc = ['En Proceso','Resuelta','Cerrada']
                n_est_inc = col_x.selectbox("Nuevo estado", estados_inc)
                if col_y.button("Cambiar Estado"):
                    model_incidencia.cambiar_estado(id_inc, n_est_inc)
                    st.success("Estado actualizado.")
                    st.rerun()

                # Agregar detalle
                with st.form("form_det_inc"):
                    st.subheader("Agregar Detalle a Incidencia")
                    desc_det = st.text_area("Descripción adicional")
                    accion   = st.text_area("Acción tomada")
                    if st.form_submit_button("Guardar Detalle"):
                        model_incidencia.create_detalle(id_inc, desc_det, accion)
                        st.success("Detalle agregado.")
                        st.rerun()

            # Exportar PDF
            if st.button("📄 Exportar Incidencias a PDF"):
                pdf_bytes = generar_pdf_incidencias(id_ev2, ev_sel2, incidencias)
                st.download_button("⬇️ Descargar PDF", data=pdf_bytes, file_name=f"incidencias_{id_ev2}.pdf", mime="application/pdf")

        else:
            st.info("No hay incidencias registradas para este evento.")

        with st.form("form_nueva_inc"):
            st.subheader("Registrar Nueva Incidencia")
            tipo_inc = st.selectbox("Tipo", ["Técnica","Logística","Personal","Climática","Seguridad","Otra"])
            desc_inc = st.text_area("Descripción *")
            desc_det_nuevo = st.text_area("Detalle inicial / acción tomada")
            if st.form_submit_button("Registrar Incidencia"):
                if not desc_inc:
                    st.error("La descripción es obligatoria.")
                else:
                    if model_incidencia.create(id_ev2, tipo_inc, desc_inc):
                        inc_rows = model_incidencia.get_by_evento(id_ev2)
                        if inc_rows and desc_det_nuevo:
                            last_id = inc_rows[-1][0]
                            model_incidencia.create_detalle(last_id, desc_inc, desc_det_nuevo)
                        st.success("Incidencia registrada.")
                        st.rerun()

    # ── TAB 3: Pagos ──────────────────────────────────────────
    with tab3:
        ev_sel3 = st.selectbox("Evento", list(ev_opciones.keys()), key="pago_ev")
        id_ev3  = ev_opciones[ev_sel3]

        pagos = model_pago.get_by_evento(id_ev3)
        if pagos:
            df_pag = pd.DataFrame(pagos, columns=["ID","Contrato","Tipo","Monto","Fecha","Estado"])
            df_pag["Monto"] = df_pag["Monto"].apply(format_currency)
            st.dataframe(df_pag, use_container_width=True)

        contratos_p = model_contrato.get_by_evento(id_ev3)
        ct_op = {"— Sin contrato —": None}
        ct_op.update({f"Contrato {c[1]} (ID:{c[0]})": c[0] for c in contratos_p})

        with st.form("form_nuevo_pago"):
            st.subheader("Registrar Pago")
            ct_sel   = st.selectbox("Contrato (opcional)", list(ct_op.keys()))
            tipo_pago = st.selectbox("Tipo de pago", model_pago.TIPOS_PAGO)
            monto_pag = st.number_input("Monto S/ *", min_value=0.01)
            fecha_pag = st.date_input("Fecha del pago", value=date.today())
            if st.form_submit_button("Registrar Pago"):
                id_ct = ct_op[ct_sel]
                if model_pago.create(id_ev3, id_ct, tipo_pago, monto_pag, fecha_pag):
                    st.success("Pago registrado.")
                    st.rerun()

    # ── TAB 4: Encuestas ──────────────────────────────────────
    with tab4:
        ev_sel4 = st.selectbox("Evento", list(ev_opciones.keys()), key="enc_ev")
        id_ev4  = ev_opciones[ev_sel4]

        encuestas_ev = model_encuesta.get_by_evento(id_ev4)
        if encuestas_ev:
            df_enc = pd.DataFrame(encuestas_ev, columns=["ID","Fecha","Satisfacción (1-5)","Estado","Comentarios"])
            st.dataframe(df_enc, use_container_width=True)

            id_enc = st.number_input("ID encuesta para ver detalle", min_value=1, step=1)
            enc = model_encuesta.get_by_id(int(id_enc))
            if enc:
                detalles_enc = model_encuesta.get_detalles(id_enc)
                if detalles_enc:
                    dimensiones = [d[1] for d in detalles_enc]
                    valores     = [d[2] for d in detalles_enc]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=valores + [valores[0]],
                        theta=dimensiones + [dimensiones[0]],
                        fill='toself', name='Satisfacción'
                    ))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,5])),
                                      title="Radar de Satisfacción")
                    st.plotly_chart(fig, use_container_width=True)
                    prom = sum(valores) / len(valores)
                    st.metric("Promedio de satisfacción", f"{prom:.1f} / 5")

        st.divider()
        with st.form("form_nueva_enc"):
            st.subheader("Nueva Encuesta de Satisfacción")
            fecha_enc = st.date_input("Fecha de evaluación", value=date.today())
            nivel_gen  = st.slider("Satisfacción general (1-5)", 1, 5, 4)
            comentarios = st.text_area("Comentarios generales")

            st.subheader("Respuestas por dimensión")
            respuestas = {}
            for dim in model_encuesta.DIMENSIONES:
                respuestas[dim] = st.slider(dim, 1, 5, 4, key=f"dim_{dim}")

            if st.form_submit_button("Guardar Encuesta"):
                id_enc_nuevo = model_encuesta.create(id_ev4, fecha_enc, nivel_gen, comentarios)
                if id_enc_nuevo:
                    for dim, resp in respuestas.items():
                        model_encuesta.create_detalle(id_enc_nuevo, dim, resp)
                    model_encuesta.completar_encuesta(id_enc_nuevo)
                    st.success("Encuesta registrada y completada.")
                    st.rerun()


def generar_pdf_incidencias(id_evento, nombre_evento, incidencias):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Incidencias", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Evento: {nombre_evento}", ln=True)
    pdf.cell(0, 8, f"Generado: {date.today()}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "=" * 60, ln=True)
    for row in incidencias:
        inc_id, tipo, desc, fecha, estado = row
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, f"[{inc_id}] {tipo} - Estado: {estado}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, f"Desc: {desc}")
        pdf.cell(0, 6, f"Fecha: {fecha}", ln=True)
        pdf.ln(3)

    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    return bytes(pdf_output)
