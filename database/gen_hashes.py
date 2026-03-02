"""
Script auxiliar para generar hashes bcrypt e insertar usuarios de prueba.
Ejecutar: python database/gen_hashes.py
Luego copiar las sentencias INSERT y ejecutarlas en PostgreSQL.
"""
import bcrypt

usuarios = [
    ("Carlos",   "Mendoza",   "admin@eventos.com",       "admin",        "Admin2024!",    "Administrador"),
    ("María",    "Torres",    "jefeeventos@eventos.com", "jefe_eventos", "Eventos2024!",  "Jefe de Eventos"),
    ("Luis",     "Ramírez",   "jefeplan@eventos.com",    "jefe_plan",    "Plan2024!",     "Jefe de Planificación"),
    ("Ana",      "Vásquez",   "jefelogist@eventos.com",  "jefe_logist",  "Logist2024!",   "Jefe de Logística"),
    ("Patricia", "Gutiérrez", "secretaria@eventos.com",  "secretaria",   "Secret2024!",   "Secretaria de Eventos"),
]

print("-- INSERT generado con bcrypt (cost=12)")
print("INSERT INTO usuarios (nombre, apellido, email, user_login, password_hash, rol) VALUES")
inserts = []
for nombre, apellido, email, login, password, rol in usuarios:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    inserts.append(f"  ('{nombre}', '{apellido}', '{email}', '{login}', '{hashed}', '{rol}')")
print(",\n".join(inserts) + ";")
