import re
from datetime import datetime
import streamlit as st

def validate_email(email: str) -> bool:
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return bool(re.match(pattern, email))

def format_currency(value) -> str:
    if value is None:
        return "S/ 0.00"
    return f"S/ {float(value):,.2f}"

def format_date(d) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        return d
    return d.strftime("%d/%m/%Y")

def generar_nro_contrato(correlativo: int) -> str:
    today = datetime.now().strftime("%Y%m%d")
    return f"CTR-{today}-{correlativo:03d}"

def paginate_dataframe(df, page_size=20):
    if df is None or len(df) == 0:
        return df, 1, 1

    total_pages = max(1, (len(df) + page_size - 1) // page_size)
    page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * page_size
    end = start + page_size
    st.caption(f"Mostrando {start + 1}–{min(end, len(df))} de {len(df)} registros | Página {page}/{total_pages}")
    return df.iloc[start:end], page, total_pages
