-- ============================================================
-- Sistema de Gestión de Eventos - Datos de Prueba
-- ============================================================
-- Contraseñas en texto claro (solo para referencia):
--   admin        -> Admin2024!
--   jefe_eventos -> Eventos2024!
--   jefe_plan    -> Plan2024!
--   jefe_logist  -> Logist2024!
--   secretaria   -> Secret2024!
-- ============================================================

-- Los hashes bcrypt a continuación corresponden a las contraseñas indicadas
-- (cost factor 12, generados con bcrypt.hashpw)

INSERT INTO usuarios (nombre, apellido, email, user_login, password_hash, rol, estado) VALUES
('Carlos',   'Mendoza',   'admin@eventos.com',       'admin',        '$2b$12$Yp8BZptj5ml1yqQQOiw2GeMl/jaT1wlAZvrgPUyrjMCg8UbX81IMO', 'Administrador',         'Activo'),
('María',    'Torres',    'jefeeventos@eventos.com', 'jefe_eventos', '$2b$12$NMvkVqjgH8NDap53xmjLy.4QVBFg2bkS7BkfNADBgn5naFmmyJ1dq',  'Jefe de Eventos',       'Activo'),
('Luis',     'Ramírez',   'jefeplan@eventos.com',    'jefe_plan',    '$2b$12$numB3/uRluXTXKfSC1p7mOYRac2qw24Cif2XYI9G5eFyfCjq28bUa',  'Jefe de Planificación', 'Activo'),
('Ana',      'Vásquez',   'jefelogist@eventos.com',  'jefe_logist',  '$2b$12$jjPxMvAO2yMN5Z.OAHenq.YqiFk2xs/MPokmbIdaJDCIIn40tRPx6',  'Jefe de Logística',     'Activo'),
('Patricia', 'Gutiérrez', 'secretaria@eventos.com',  'secretaria',   '$2b$12$wNjqtsOLKUfjvAFn/rUvb.g6ey7p0BQMMzMztX9XVB/EvNbdxoFk2',  'Secretaria de Eventos', 'Activo');

-- 5 clientes
INSERT INTO clientes (nombre, tipo_cliente, direccion, email, telefono, estado) VALUES
('Empresa ABC S.A.',         'Empresa',         'Av. Principal 123, Lima',       'contacto@abc.com',       '01-4567890', 'Activo'),
('Juan Carlos Pérez',        'Persona Natural', 'Jr. Las Flores 456, Lima',      'jcperez@gmail.com',      '987654321',  'Activo'),
('Municipalidad de Miraflores', 'Institución',  'Av. Larco 400, Miraflores',     'eventos@miraflores.gob.pe','01-6171717','Activo'),
('StartupTech EIRL',         'Empresa',         'Calle Innovación 789, San Isidro','hola@startuptech.pe',  '01-2223333', 'Activo'),
('Rosa María Flores',        'Persona Natural', 'Urb. Santa Rosa 321, Surco',    'rmflores@outlook.com',   '976543210',  'Activo');

-- 2 proveedores
INSERT INTO proveedores (nombre, tipo_servicio, disponibilidad, email, telefono) VALUES
('Sonido Profesional SAC',  'Audio y Video',     TRUE, 'ventas@sonidopro.com',  '01-3456789'),
('Catering Delicias EIRL',  'Catering',          TRUE, 'info@catering.pe',      '01-9876543');

-- 3 eventos
INSERT INTO eventos (nombre, tipo_evento, lugar_evento, fecha_evento, monto_evento, estado, id_cliente) VALUES
('Lanzamiento Producto ABC',  'Corporativo', 'Hotel Westin, Lima',      CURRENT_DATE + 30, 15000.00, 'Registrada',    1),
('Boda Juan y Ana',           'Social',      'Hacienda Villa Alegre',   CURRENT_DATE + 15,  8000.00, 'En Ejecución',  2),
('Congreso Municipal 2024',   'Institucional','Centro de Convenciones', CURRENT_DATE - 10, 25000.00, 'Cerrada',       3);

-- 4 recursos (2 material, 2 logístico)
INSERT INTO recursos (nombre, tipo_recurso, cantidad, estado, id_proveedor) VALUES
('Sillas plegables',     'Material',   200, 'Disponible', NULL),
('Mesas redondas',       'Material',   30,  'Disponible', NULL),
('Camioneta de transporte', 'Logístico', 2, 'Disponible', NULL),
('Equipo de sonido',     'Logístico',  1,   'Asignado',   1);

-- 1 contrato aprobado, 1 pendiente
INSERT INTO contratos (nro_contrato, id_evento, id_proveedor, fecha_contrato, estado_contrato, monto, descripcion, firma_digital) VALUES
('CTR-20240101-001', 2, 1, CURRENT_DATE - 5, 'Aprobado',  3500.00, 'Servicio de sonido para boda', TRUE),
('CTR-20240101-002', 1, 2, CURRENT_DATE,     'Pendiente', 4500.00, 'Servicio de catering lanzamiento', FALSE);

-- 1 plan aprobado
INSERT INTO plan_evento (id_evento, fecha_elaboracion, presupuesto, estado, descripcion) VALUES
(1, CURRENT_DATE - 2, 14000.00, 'Aprobado', 'Plan completo para lanzamiento de producto ABC');

-- Requerimientos de evento
INSERT INTO requerimientos_evento (id_evento, descripcion, tipo_recurso, cantidad) VALUES
(1, 'Sillas para 150 personas',  'Material',  150),
(1, 'Equipo de sonido profesional', 'Logístico', 1),
(2, 'Mesas para 20 invitados',   'Material',   20);

-- Cotizacion
INSERT INTO cotizacion_proveedor (id_proveedor, id_evento, fecha_generado, monto, estado, descripcion) VALUES
(1, 1, CURRENT_DATE - 1, 3500.00, 'Aceptada', 'Cotización equipos de audio y video');

-- 1 orden de compra aprobada
INSERT INTO ordenes_compra (id_evento, id_proveedor, id_recurso, id_cotizacion, fecha, estado, monto) VALUES
(1, 1, 4, 1, CURRENT_DATE - 1, 'Aprobada', 3500.00);

-- Asignación
INSERT INTO asignacion_recurso (id_evento, id_recurso, cantidad, fecha_asignacion, estado) VALUES
(2, 4, 1, CURRENT_DATE - 3, 'Confirmada');

-- 1 incidencia con detalle
INSERT INTO incidencias (id_evento, tipo_incidencia, descripcion, estado) VALUES
(2, 'Técnica', 'Falla en equipo de sonido durante ceremonia', 'Resuelta');

INSERT INTO detalle_incidencia (id_incidencia, descripcion, accion_tomada) VALUES
(1, 'El amplificador principal dejó de funcionar a mitad del evento', 'Se reemplazó con equipo de respaldo disponible en el vehículo del proveedor');

-- Pagos
INSERT INTO pagos (id_evento, id_contrato, tipo_pago, monto, fecha_pago, estado) VALUES
(2, 1, 'Normal',    2000.00, CURRENT_DATE - 10, 'Pagado'),
(2, 1, 'Adicional',  500.00, CURRENT_DATE - 2,  'Pagado');

-- 1 encuesta respondida
INSERT INTO encuestas (id_evento, fecha_evaluacion, nivel_satisfaccion, estado_evaluacion, comentarios) VALUES
(3, CURRENT_DATE - 9, 4, 'Completada', 'Excelente organización, pequeños retrasos en inicio');

INSERT INTO detalle_encuesta (id_encuesta, pregunta, respuesta) VALUES
(1, 'Calidad del servicio',    4),
(1, 'Cumplimiento del programa', 4),
(1, 'Recursos disponibles',   5),
(1, 'Comunicación previa',    4);