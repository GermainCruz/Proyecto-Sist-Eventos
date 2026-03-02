import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "bd_genesis")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "sa")

APP_TITLE = "Sistema de Gestión de Eventos"
APP_ICON = "🎪"

ROLES = [
    "Administrador",
    "Jefe de Eventos",
    "Jefe de Planificación",
    "Jefe de Logística",
    "Secretaria de Eventos",
]

ESTADOS_EVENTO = [
    "Registrada",
    "En Planificación",
    "Plan Aprobado",
    "Confirmada",
    "En Ejecución",
    "Cerrada",
    "Cancelada",
]
