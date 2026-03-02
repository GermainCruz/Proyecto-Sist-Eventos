import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from config import APP_TITLE, APP_ICON
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Verificar sesión ─────────────────────────────────────────
if not st.session_state.get("autenticado", False):
    from auth.login import show_login
    show_login()
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────
rol = st.session_state.get("rol", "")
nombre = st.session_state.get("nombre", "")
apellido = st.session_state.get("apellido", "")

with st.sidebar:
    st.markdown(f"### 🎪 {APP_TITLE}")
    st.divider()
    st.markdown(f"👤 **{nombre} {apellido}**")
    st.caption(f"Rol: {rol}")
    st.divider()

    # Definir menú según rol
    menu_base = {
        "📊 Dashboard":            "dashboard",
        "👥 Clientes":             "clientes",
        "📄 Contratos":            "contratos",
        "📋 Planificación":        "planificacion",
        "📦 Recursos y Proveedores": "recursos",
        "🚀 Ejecución y Cierre":   "ejecucion",
    }

    if rol == "Administrador":
        menu_base["🔧 Administración"] = "admin"
    elif rol == "Jefe de Eventos":
        allowed = {"📊 Dashboard", "👥 Clientes", "📄 Contratos", "📋 Planificación", "🚀 Ejecución y Cierre"}
        menu_base = {k: v for k, v in menu_base.items() if k in allowed}
    elif rol == "Jefe de Planificación":
        allowed = {"📊 Dashboard", "📋 Planificación"}
        menu_base = {k: v for k, v in menu_base.items() if k in allowed}
    elif rol == "Jefe de Logística":
        allowed = {"📊 Dashboard", "📦 Recursos y Proveedores", "🚀 Ejecución y Cierre"}
        menu_base = {k: v for k, v in menu_base.items() if k in allowed}
    elif rol == "Secretaria de Eventos":
        # La Secretaria solo ve Dashboard y su módulo propio (CU1 completo):
        # clientes, eventos, requerimientos y contratos.
        # No debe ver Planificación, Recursos ni Ejecución.
        menu_base = {
            "📊 Dashboard":                          "dashboard",
            "🗂️ Clientes, Eventos y Contratos":     "secretaria",
        }

    pagina_label = st.radio("Navegación", list(menu_base.keys()), label_visibility="collapsed")
    pagina = menu_base[pagina_label]

    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Enrutar a la página seleccionada ─────────────────────────
if pagina == "dashboard":
    from shared.page_dashboard import show
    show()

elif pagina == "clientes":
    from cu1_contratos.page_clientes import show
    show()

elif pagina == "contratos":
    from cu1_contratos.page_contratos import show
    show()

elif pagina == "planificacion":
    from cu2_planificacion.page_planificacion import show
    show()

elif pagina == "recursos":
    from cu3_recursos.page_recursos import show
    show()

elif pagina == "ejecucion":
    from cu4_ejecucion.page_ejecucion import show
    show()

elif pagina == "secretaria":
    from cu1_contratos.page_secretaria import show
    show()

elif pagina == "admin":
    from shared.page_admin import show
    show()
