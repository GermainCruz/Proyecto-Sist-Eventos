# 🎪 Sistema de Gestión de Eventos (ProySistemaEventos)

Aplicación web completa para gestionar el ciclo de vida de eventos: contratos, planificación, recursos/proveedores y ejecución/cierre.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend/Backend | Python 3.11+ con Streamlit |
| Base de datos | PostgreSQL 17 |
| Driver BD | psycopg2-binary |
| Autenticación | bcrypt + st.session_state |
| Visualización | Plotly 5.17.0 |
| Exportación PDF | fpdf 1.7.2 |
| Variables de entorno | python-dotenv 1.0.0 |

## Prerrequisitos

- Python 3.11+
- PostgreSQL 17
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd sist_eventos

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Configuración del entorno

Crea el archivo `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bd_genesis
DB_USER=postgres
DB_PASS=sa
```

## Configurar la Base de Datos

```bash
# Crear la base de datos
createdb -U postgres bd_genesis

# Aplicar el schema
psql -U postgres -d bd_genesis -f database/schema.sql

# Cargar datos de prueba
psql -U postgres -d bd_genesis -f database/seed.sql
```

> **Nota**: Los hashes bcrypt del seed.sql fueron generados con un cost factor de 12. Si necesitas regenerar contraseñas, usa el script incluido en `database/gen_hashes.py`.

## Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación abrirá automáticamente en `http://localhost:8501`

## Usuarios de Prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `Admin2024!` | Administrador |
| `jefe_eventos` | `Eventos2024!` | Jefe de Eventos |
| `jefe_plan` | `Plan2024!` | Jefe de Planificación |
| `jefe_logist` | `Logist2024!` | Jefe de Logística |
| `secretaria` | `Secret2024!` | Secretaria de Eventos |

> **Importante**: El seed.sql contiene hashes bcrypt pre-generados. Si los hashes no funcionan (versión de bcrypt diferente), ejecuta el script auxiliar: `python database/gen_hashes.py` para regenerarlos e insertar los usuarios manualmente.

## Módulos Principales

### CU1 — Gestión de Contratos y Clientes
- Registro y búsqueda de clientes (con validación de email único).
- Generación de contratos con número automático (CTR-YYYYMMDD-NNN).
- Flujo: Pendiente → Aprobado/Rechazado → Firmado → Cumplido.

### CU2 — Gestión de Planificación
- Registro de eventos y asignación a clientes.
- Elaboración de planes con presupuesto y flujo de aprobación.
- Gestión de requerimientos y verificación de disponibilidad de recursos.
- Cotizaciones de proveedores.

### CU3 — Gestión de Recursos y Proveedores
- CRUD de proveedores y recursos.
- Asignación de recursos a eventos.
- Órdenes de compra con flujo completo: Pendiente → En Revisión → Aprobada → Enviada → Recibida.

### CU4 — Ejecución y Cierre
- Supervisión del evento (cambio de estados).
- Registro de incidencias con detalle y acciones tomadas.
- Registro de pagos (Normal, Adicional, Restante).
- Encuestas de satisfacción por dimensión con gráfico radar.
- Exportación de reporte de incidencias a PDF.

## Estructura del Proyecto

```
sist_eventos/
├── app.py                          # Punto de entrada y navegación
├── config.py                       # Configuración global
├── requirements.txt
├── README.md
├── .env
├── database/
│   ├── connection.py               # Pool de conexiones PostgreSQL
│   ├── schema.sql                  # DDL completo
│   └── seed.sql                    # Datos de prueba
├── auth/
│   ├── login.py                    # Formulario de login
│   └── roles.py                    # Control de acceso por rol
├── cu1_contratos/                  # CU1: Contratos y Clientes
├── cu2_planificacion/              # CU2: Planificación
├── cu3_recursos/                   # CU3: Recursos y Proveedores
├── cu4_ejecucion/                  # CU4: Ejecución y Cierre
└── shared/                         # Componentes compartidos
```
