import streamlit as st
import pandas as pd
from datetime import date
from auth.roles import requiere_rol, check_rol
from cu2_planificacion import model_evento, model_plan_evento, model_requerimiento, model_cotizacion
from cu3_recursos import model_proveedor, model_recurso, model_orden_compra
from shared.utils import format_currency

def show():
    requiere_rol(['Administrador', 'Jefe de Planificación', 'Jefe de Eventos'])
    st.title("📋 Gestión de Planificación de Eventos")

    tab1, tab2, tab3, tab4 = st.tabs(["📅 Eventos", "📝 Plan del Evento", "📦 Requerimientos", "💰 Cotizaciones"])

    # ── TAB 1: Eventos ────────────────────────────────────────
    with tab1:
        st.subheader("Registrar Nuevo Evento")
        clientes_rows = []
        from cu1_contratos import model_cliente
        clientes_rows = model_cliente.get_activos()
        cli_opciones = {f"{c[1]} (ID:{c[0]})": c[0] for c in clientes_rows}

        with st.form("form_evento"):
            c1, c2 = st.columns(2)
            nombre       = c1.text_input("Nombre del evento *")
            tipo_evento  = c2.selectbox("Tipo de evento", ["Corporativo","Social","Institucional","Cultural","Deportivo","Otro"])
            lugar_evento = c1.text_input("Lugar")
            fecha_evento = c2.date_input("Fecha del evento")
            monto_evento = st.number_input("Monto estimado S/", min_value=0.0)
            cliente_sel  = st.selectbox("Cliente *", list(cli_opciones.keys()) if cli_opciones else ["Sin clientes"])
            if st.form_submit_button("Registrar Evento"):
                if not nombre or not cli_opciones:
                    st.error("Nombre y cliente son obligatorios.")
                else:
                    id_cli = cli_opciones[cliente_sel]
                    if model_evento.create(nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, id_cli):
                        st.success(f"Evento '{nombre}' registrado.")
                        st.rerun()

        st.divider()
        st.subheader("Listado de Eventos")
        rows = model_evento.get_all()
        if rows:
            df = pd.DataFrame(rows, columns=["ID","Nombre","Tipo","Lugar","Fecha","Monto","Estado","Cliente"])
            st.dataframe(df, use_container_width=True)

            if check_rol(['Administrador','Jefe de Eventos']):
                st.subheader("Cambiar Estado del Evento")
                from config import ESTADOS_EVENTO
                id_ev = st.number_input("ID del evento", min_value=1, step=1, key="ev_estado_id")
                nuevo_est = st.selectbox("Nuevo estado", ESTADOS_EVENTO, key="ev_estado_sel")
                if st.button("Actualizar Estado"):
                    if model_evento.cambiar_estado(int(id_ev), nuevo_est):
                        st.success("Estado actualizado.")
                        st.rerun()

    # ── TAB 2: Plan del Evento ────────────────────────────────
    with tab2:
        eventos_activos = model_evento.get_activos()
        if not eventos_activos:
            st.warning("No hay eventos activos.")
        else:
            ev_opciones = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_activos}
            ev_sel = st.selectbox("Seleccionar Evento", list(ev_opciones.keys()), key="plan_ev_sel")
            id_ev_sel = ev_opciones[ev_sel]

            planes = model_plan_evento.get_by_evento(id_ev_sel)
            if planes:
                st.subheader("Planes registrados")
                df_plan = pd.DataFrame(planes, columns=["ID","Fecha Elab.","Presupuesto","Estado","Descripción"])
                df_plan["Presupuesto"] = df_plan["Presupuesto"].apply(format_currency)
                st.dataframe(df_plan, use_container_width=True)

                id_plan = st.number_input("ID del plan a gestionar", min_value=1, step=1)
                plan = model_plan_evento.get_by_id(int(id_plan))
                if plan:
                    (pid, pev, pfecha, ppres, pest, pdesc) = plan
                    st.info(f"Estado actual: **{pest}**")
                    col1, col2, col3, col4 = st.columns(4)
                    if pest == 'Borrador':
                        if col1.button("📤 Enviar a Revisión"):
                            model_plan_evento.cambiar_estado(pid, 'En Revisión')
                            st.rerun()
                    if pest == 'En Revisión' and check_rol(['Administrador','Jefe de Eventos']):
                        if col2.button("✅ Aprobar Plan"):
                            model_plan_evento.cambiar_estado(pid, 'Aprobado')
                            model_evento.cambiar_estado(pev, 'Plan Aprobado')
                            st.success("Plan aprobado.")
                            st.rerun()
                        if col3.button("🔄 Solicitar Ajustes"):
                            model_plan_evento.cambiar_estado(pid, 'Rechazado')
                            st.warning("Se solicitaron ajustes al plan.")
                            st.rerun()
                    if pest == 'Aprobado':
                        if col4.button("📌 Confirmar Planificación"):
                            model_plan_evento.cambiar_estado(pid, 'Registrado')
                            model_evento.cambiar_estado(pev, 'Confirmada')
                            st.success("Planificación confirmada. Evento listo para ejecución.")
                            st.rerun()

            st.divider()
            st.subheader("Elaborar Nuevo Plan")
            with st.form("form_nuevo_plan"):
                fecha_elab  = st.date_input("Fecha de elaboración", value=date.today())
                presupuesto = st.number_input("Presupuesto S/", min_value=0.0, step=100.0)
                descripcion = st.text_area("Descripción del plan")
                if st.form_submit_button("Guardar Plan"):
                    if model_plan_evento.create(id_ev_sel, fecha_elab, presupuesto, descripcion):
                        st.success("Plan creado.")
                        st.rerun()

    # ── TAB 3: Requerimientos ─────────────────────────────────
    with tab3:
        eventos_r = model_evento.get_activos()
        if not eventos_r:
            st.warning("No hay eventos activos.")
        else:
            ev_op_r = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_r}
            ev_sel_r = st.selectbox("Evento", list(ev_op_r.keys()), key="req_ev_sel")
            id_ev_r  = ev_op_r[ev_sel_r]

            reqs = model_requerimiento.get_by_evento(id_ev_r)
            if reqs:
                df_req = pd.DataFrame(reqs, columns=["ID","Descripción","Tipo Recurso","Cantidad"])
                st.dataframe(df_req, use_container_width=True)

                # Verificar disponibilidad
                st.subheader("Verificar Disponibilidad Interna")
                for req in reqs:
                    disponibles = model_recurso.get_disponibles_por_tipo(req[2])
                    total_disp = sum(r[2] for r in disponibles)
                    if total_disp >= req[3]:
                        st.success(f"✅ {req[1]}: {total_disp} disponibles (necesita {req[3]})")
                    else:
                        st.warning(f"⚠️ {req[1]}: solo {total_disp} disponibles (necesita {req[3]}) — considerar cotización")
            else:
                st.info("No hay requerimientos para este evento.")

            st.divider()
            with st.form("form_nuevo_req"):
                st.subheader("Agregar Requerimiento")
                desc_r   = st.text_input("Descripción *")
                tipo_r   = st.selectbox("Tipo de recurso", model_requerimiento.TIPOS_RECURSO)
                cant_r   = st.number_input("Cantidad", min_value=1, step=1)
                if st.form_submit_button("Agregar"):
                    if not desc_r:
                        st.error("La descripción es obligatoria.")
                    elif model_requerimiento.create(id_ev_r, desc_r, tipo_r, cant_r):
                        st.success("Requerimiento agregado.")
                        st.rerun()

    # ── TAB 4: Cotizaciones ───────────────────────────────────
    with tab4:
        eventos_c = model_evento.get_activos()
        ev_op_c   = {f"{e[1]} (ID:{e[0]})": e[0] for e in eventos_c}
        ev_sel_c  = st.selectbox("Evento", list(ev_op_c.keys()), key="cot_ev_sel")
        id_ev_c   = ev_op_c[ev_sel_c]

        cots = model_cotizacion.get_by_evento(id_ev_c)
        if cots:
            df_cot = pd.DataFrame(cots, columns=["ID","Proveedor","Fecha","Monto","Estado","Descripción"])
            df_cot["Monto"] = df_cot["Monto"].apply(format_currency)
            st.dataframe(df_cot, use_container_width=True)

            id_cot = st.number_input("ID cotización", min_value=1, step=1)
            cot = model_cotizacion.get_by_id(int(id_cot))
            if cot and cot[5] == 'Pendiente':
                c1, c2 = st.columns(2)
                if c1.button("✅ Aceptar Cotización"):
                    model_cotizacion.cambiar_estado(id_cot, 'Aceptada')
                    st.success("Cotización aceptada. Puedes generar la OC en el módulo de Recursos.")
                    st.rerun()
                if c2.button("❌ Rechazar Cotización"):
                    model_cotizacion.cambiar_estado(id_cot, 'Rechazada')
                    st.warning("Cotización rechazada.")
                    st.rerun()

        st.divider()
        proveedores = model_proveedor.get_all()
        prov_op = {f"{p[1]} (ID:{p[0]})": p[0] for p in proveedores}
        with st.form("form_nueva_cot"):
            st.subheader("Registrar Cotización")
            prov_sel = st.selectbox("Proveedor *", list(prov_op.keys()))
            fecha_c  = st.date_input("Fecha", value=date.today())
            monto_c  = st.number_input("Monto S/", min_value=0.0)
            desc_c   = st.text_area("Descripción")
            if st.form_submit_button("Guardar Cotización"):
                id_prov_c = prov_op[prov_sel]
                if model_cotizacion.create(id_prov_c, id_ev_c, fecha_c, monto_c, desc_c):
                    st.success("Cotización registrada.")
                    st.rerun()
