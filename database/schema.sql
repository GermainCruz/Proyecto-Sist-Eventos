-- ============================================================
-- Sistema de Gestión de Eventos - Schema PostgreSQL 17
-- ============================================================

-- Trigger function para updated_at automático
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TABLA: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre          VARCHAR(100) NOT NULL,
    apellido        VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    user_login      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(50)  NOT NULL CHECK (rol IN (
                        'Administrador','Jefe de Eventos',
                        'Jefe de Planificación','Jefe de Logística',
                        'Secretaria de Eventos')),
    estado          VARCHAR(20)  NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol   ON usuarios(rol);
CREATE TRIGGER trg_usuarios_updated_at
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: clientes
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente      INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre          VARCHAR(200) NOT NULL,
    tipo_cliente    VARCHAR(50)  NOT NULL CHECK (tipo_cliente IN ('Persona Natural','Empresa','Institución')),
    direccion       VARCHAR(300),
    email           VARCHAR(150) NOT NULL UNIQUE,
    telefono        VARCHAR(30),
    fecha_registro  DATE NOT NULL DEFAULT CURRENT_DATE,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_clientes_email  ON clientes(email);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);
CREATE TRIGGER trg_clientes_updated_at
    BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: proveedores
-- ============================================================
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor    INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre          VARCHAR(200) NOT NULL,
    tipo_servicio   VARCHAR(100) NOT NULL,
    disponibilidad  BOOLEAN NOT NULL DEFAULT TRUE,
    email           VARCHAR(150),
    telefono        VARCHAR(30),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON proveedores(nombre);
CREATE TRIGGER trg_proveedores_updated_at
    BEFORE UPDATE ON proveedores
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: eventos
-- ============================================================
CREATE TABLE IF NOT EXISTS eventos (
    id_evento       INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre          VARCHAR(200) NOT NULL,
    tipo_evento     VARCHAR(100) NOT NULL,
    lugar_evento    VARCHAR(300),
    fecha_evento    DATE,
    monto_evento    NUMERIC(12,2),
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Registrada' CHECK (estado IN (
                        'Registrada','En Planificación','Plan Aprobado',
                        'Confirmada','En Ejecución','Cerrada','Cancelada')),
    id_cliente      INTEGER NOT NULL REFERENCES clientes(id_cliente) ON DELETE RESTRICT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_eventos_estado     ON eventos(estado);
CREATE INDEX IF NOT EXISTS idx_eventos_cliente    ON eventos(id_cliente);
CREATE INDEX IF NOT EXISTS idx_eventos_fecha      ON eventos(fecha_evento);
CREATE TRIGGER trg_eventos_updated_at
    BEFORE UPDATE ON eventos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: requerimientos_evento
-- ============================================================
CREATE TABLE IF NOT EXISTS requerimientos_evento (
    id_requerimiento INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento        INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    descripcion      TEXT NOT NULL,
    tipo_recurso     VARCHAR(50) NOT NULL CHECK (tipo_recurso IN ('Material','Logístico','Personal','Tecnológico','Otro')),
    cantidad         INTEGER NOT NULL DEFAULT 1,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_req_evento ON requerimientos_evento(id_evento);

-- ============================================================
-- TABLA: plan_evento
-- ============================================================
CREATE TABLE IF NOT EXISTS plan_evento (
    id_plan_evento    INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento         INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    fecha_elaboracion DATE NOT NULL DEFAULT CURRENT_DATE,
    presupuesto       NUMERIC(12,2),
    estado            VARCHAR(30) NOT NULL DEFAULT 'Borrador' CHECK (estado IN (
                          'Borrador','En Revisión','Aprobado','Rechazado','Registrado')),
    descripcion       TEXT,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plan_evento ON plan_evento(id_evento);
CREATE TRIGGER trg_plan_evento_updated_at
    BEFORE UPDATE ON plan_evento
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: contratos
-- ============================================================
CREATE TABLE IF NOT EXISTS contratos (
    id_contrato     INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nro_contrato    VARCHAR(30)  NOT NULL UNIQUE,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    id_proveedor    INTEGER NOT NULL REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT,
    fecha_contrato  DATE NOT NULL DEFAULT CURRENT_DATE,
    estado_contrato VARCHAR(30)  NOT NULL DEFAULT 'Pendiente' CHECK (estado_contrato IN (
                        'Pendiente','Aprobado','Rechazado','Firmado','Cumplido')),
    monto           NUMERIC(12,2),
    descripcion     TEXT,
    firma_digital   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contratos_evento    ON contratos(id_evento);
CREATE INDEX IF NOT EXISTS idx_contratos_proveedor ON contratos(id_proveedor);
CREATE INDEX IF NOT EXISTS idx_contratos_estado    ON contratos(estado_contrato);
CREATE TRIGGER trg_contratos_updated_at
    BEFORE UPDATE ON contratos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: recursos
-- ============================================================
CREATE TABLE IF NOT EXISTS recursos (
    id_recurso      INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre          VARCHAR(200) NOT NULL,
    tipo_recurso    VARCHAR(50)  NOT NULL CHECK (tipo_recurso IN ('Material','Logístico','Personal','Tecnológico','Otro')),
    cantidad        INTEGER NOT NULL DEFAULT 0,
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Disponible' CHECK (estado IN ('Disponible','Asignado','No Disponible','Mantenimiento')),
    id_proveedor    INTEGER REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_recursos_estado ON recursos(estado);
CREATE TRIGGER trg_recursos_updated_at
    BEFORE UPDATE ON recursos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: cotizacion_proveedor
-- ============================================================
CREATE TABLE IF NOT EXISTS cotizacion_proveedor (
    id_cotizacion   INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_proveedor    INTEGER NOT NULL REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    fecha_generado  DATE NOT NULL DEFAULT CURRENT_DATE,
    monto           NUMERIC(12,2),
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente','Aceptada','Rechazada')),
    descripcion     TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cotizacion_evento    ON cotizacion_proveedor(id_evento);
CREATE INDEX IF NOT EXISTS idx_cotizacion_proveedor ON cotizacion_proveedor(id_proveedor);
CREATE TRIGGER trg_cotizacion_updated_at
    BEFORE UPDATE ON cotizacion_proveedor
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: ordenes_compra
-- ============================================================
CREATE TABLE IF NOT EXISTS ordenes_compra (
    id_orden_compra INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    id_proveedor    INTEGER NOT NULL REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT,
    id_recurso      INTEGER NOT NULL REFERENCES recursos(id_recurso) ON DELETE RESTRICT,
    id_cotizacion   INTEGER REFERENCES cotizacion_proveedor(id_cotizacion) ON DELETE RESTRICT,
    fecha           DATE NOT NULL DEFAULT CURRENT_DATE,
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Pendiente' CHECK (estado IN (
                        'Pendiente','En Revisión','Aprobada','Rechazada','Enviada','Recibida')),
    monto           NUMERIC(12,2),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_oc_evento    ON ordenes_compra(id_evento);
CREATE INDEX IF NOT EXISTS idx_oc_proveedor ON ordenes_compra(id_proveedor);
CREATE INDEX IF NOT EXISTS idx_oc_estado    ON ordenes_compra(estado);
CREATE TRIGGER trg_oc_updated_at
    BEFORE UPDATE ON ordenes_compra
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: asignacion_recurso
-- ============================================================
CREATE TABLE IF NOT EXISTS asignacion_recurso (
    id_asignacion   INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    id_recurso      INTEGER NOT NULL REFERENCES recursos(id_recurso) ON DELETE RESTRICT,
    cantidad        INTEGER NOT NULL DEFAULT 1,
    fecha_asignacion DATE NOT NULL DEFAULT CURRENT_DATE,
    estado          VARCHAR(30) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente','Confirmada','Cancelada')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_asignacion_evento   ON asignacion_recurso(id_evento);
CREATE INDEX IF NOT EXISTS idx_asignacion_recurso  ON asignacion_recurso(id_recurso);

-- ============================================================
-- TABLA: incidencias
-- ============================================================
CREATE TABLE IF NOT EXISTS incidencias (
    id_incidencia   INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    tipo_incidencia VARCHAR(100) NOT NULL,
    descripcion     TEXT NOT NULL,
    fecha_registro  TIMESTAMP NOT NULL DEFAULT NOW(),
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Abierta' CHECK (estado IN ('Abierta','En Proceso','Resuelta','Cerrada')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_incidencias_evento ON incidencias(id_evento);
CREATE TRIGGER trg_incidencias_updated_at
    BEFORE UPDATE ON incidencias
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- TABLA: detalle_incidencia
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_incidencia (
    id_detalle_incidencia INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_incidencia         INTEGER NOT NULL REFERENCES incidencias(id_incidencia) ON DELETE RESTRICT,
    descripcion           TEXT NOT NULL,
    accion_tomada         TEXT,
    created_at            TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_det_incidencia ON detalle_incidencia(id_incidencia);

-- ============================================================
-- TABLA: pagos
-- ============================================================
CREATE TABLE IF NOT EXISTS pagos (
    id_pago         INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento       INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    id_contrato     INTEGER REFERENCES contratos(id_contrato) ON DELETE RESTRICT,
    tipo_pago       VARCHAR(30)  NOT NULL CHECK (tipo_pago IN ('Normal','Adicional','Restante')),
    monto           NUMERIC(12,2) NOT NULL,
    fecha_pago      DATE NOT NULL DEFAULT CURRENT_DATE,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente','Pagado','Anulado')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pagos_evento ON pagos(id_evento);

-- ============================================================
-- TABLA: encuestas
-- ============================================================
CREATE TABLE IF NOT EXISTS encuestas (
    id_encuesta         INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_evento           INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE RESTRICT,
    fecha_evaluacion    DATE NOT NULL DEFAULT CURRENT_DATE,
    nivel_satisfaccion  INTEGER CHECK (nivel_satisfaccion BETWEEN 1 AND 5),
    estado_evaluacion   VARCHAR(30) NOT NULL DEFAULT 'Pendiente' CHECK (estado_evaluacion IN ('Pendiente','Completada')),
    comentarios         TEXT,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_encuestas_evento ON encuestas(id_evento);

-- ============================================================
-- TABLA: detalle_encuesta
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_encuesta (
    id_detalle_encuesta INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_encuesta         INTEGER NOT NULL REFERENCES encuestas(id_encuesta) ON DELETE RESTRICT,
    pregunta            VARCHAR(200) NOT NULL,
    respuesta           INTEGER NOT NULL CHECK (respuesta BETWEEN 1 AND 5),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_det_encuesta ON detalle_encuesta(id_encuesta);