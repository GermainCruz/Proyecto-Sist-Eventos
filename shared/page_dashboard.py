import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.connection import execute_query, execute_query_one

def show():
    st.title("📊 Dashboard — Sistema de Gestión de Eventos")

    # ── KPIs ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    total_activos = (execute_query_one(
        "SELECT COUNT(*) FROM eventos WHERE estado NOT IN ('Cerrada','Cancelada')"
    ) or [0])[0]

    contratos_pend = (execute_query_one(
        "SELECT COUNT(*) FROM contratos WHERE estado_contrato = 'Pendiente'"
    ) or [0])[0]

    recursos_disp = (execute_query_one(
        "SELECT COUNT(*) FROM recursos WHERE estado = 'Disponible'"
    ) or [0])[0]

    sat_prom = execute_query_one(
        "SELECT ROUND(AVG(nivel_satisfaccion) * 20, 1) FROM encuestas WHERE estado_evaluacion = 'Completada'"
    )
    sat_prom = sat_prom[0] if sat_prom and sat_prom[0] else 0

    with col1:
        st.metric("🎪 Eventos Activos",       total_activos)
    with col2:
        st.metric("📄 Contratos Pendientes",  contratos_pend,
                  delta="⚠️ Revisar" if contratos_pend > 0 else None,
                  delta_color="inverse")
    with col3:
        st.metric("📦 Recursos Disponibles",  recursos_disp)
    with col4:
        st.metric("⭐ Satisfacción Promedio",  f"{sat_prom}%")

    st.divider()

    # ── Gráficos ──────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Eventos por Estado")
        rows = execute_query("SELECT estado, COUNT(*) FROM eventos GROUP BY estado")
        if rows:
            df_est = pd.DataFrame(rows, columns=["Estado", "Cantidad"])
            fig = px.bar(df_est, x="Estado", y="Cantidad", color="Estado",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos.")

    with col_b:
        st.subheader("Distribución por Tipo de Evento")
        rows2 = execute_query("SELECT tipo_evento, COUNT(*) FROM eventos GROUP BY tipo_evento")
        if rows2:
            df_tipo = pd.DataFrame(rows2, columns=["Tipo", "Cantidad"])
            fig2 = px.pie(df_tipo, names="Tipo", values="Cantidad",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sin datos.")

    st.divider()

    # ── Próximos eventos ──────────────────────────────────────
    st.subheader("📅 Próximos 5 Eventos")
    rows3 = execute_query(
        """SELECT e.nombre, e.tipo_evento, e.lugar_evento, e.fecha_evento,
                  e.estado, c.nombre AS cliente
           FROM eventos e
           JOIN clientes c ON e.id_cliente = c.id_cliente
           WHERE e.fecha_evento >= CURRENT_DATE
             AND e.estado NOT IN ('Cerrada','Cancelada')
           ORDER BY e.fecha_evento
           LIMIT 5"""
    )
    if rows3:
        df_prox = pd.DataFrame(rows3, columns=["Evento","Tipo","Lugar","Fecha","Estado","Cliente"])
        st.dataframe(df_prox, use_container_width=True)
    else:
        st.info("No hay próximos eventos registrados.")

    st.divider()

    # ── Alertas ───────────────────────────────────────────────
    st.subheader("🔔 Alertas")
    alerta1 = execute_query("SELECT nro_contrato FROM contratos WHERE estado_contrato = 'Pendiente'")
    alerta2 = execute_query("SELECT id_orden_compra FROM ordenes_compra WHERE estado = 'Pendiente'")

    if alerta1:
        nums = ", ".join(r[0] for r in alerta1)
        st.warning(f"⚠️ Contratos sin aprobar: {nums}")
    if alerta2:
        ids = ", ".join(str(r[0]) for r in alerta2)
        st.warning(f"⚠️ Órdenes de compra pendientes (ID): {ids}")
    if not alerta1 and not alerta2:
        st.success("✅ Sin alertas pendientes.")
