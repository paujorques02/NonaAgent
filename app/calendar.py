# calendar.py
import sqlite3
from datetime import datetime
from app.email_utils import send_email
from app.config import settings

def init_db():
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    # Tabla de reservas
    c.execute('''CREATE TABLE IF NOT EXISTS calendario (
        fecha TEXT,
        tipo_evento TEXT,
        nombre TEXT,
        email TEXT
    )''')
    # Tabla de servicios
    c.execute('''CREATE TABLE IF NOT EXISTS servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT,
        precio REAL
    )''')
    # Poblar servicios si está vacía
    c.execute('SELECT COUNT(*) FROM servicios')
    if c.fetchone()[0] == 0:
        servicios = [
            ("Decoración de bodas", "Decoración integral para bodas.", 1200),
            ("Wedding planner", "Organización completa de bodas.", 2000),
            ("Decoración de bautizos", "Decoración temática para bautizos.", 800),
            ("Decoración de comuniones", "Decoración especial para comuniones.", 900),
            ("Decoración de cumpleaños", "Decoración personalizada para cumpleaños.", 600)
        ]
        c.executemany('INSERT INTO servicios (nombre, descripcion, precio) VALUES (?,?,?)', servicios)
    conn.commit()
    conn.close()

# Consultar servicios y precios

def get_services():
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute('SELECT nombre, descripcion, precio FROM servicios')
    servicios = c.fetchall()
    conn.close()
    return servicios

def get_service_price(nombre_servicio):
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute('SELECT precio FROM servicios WHERE nombre=?', (nombre_servicio,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def create_reservation(fecha, tipo_evento, nombre, email):
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO calendario VALUES (?,?,?,?)", (fecha, tipo_evento, nombre, email))
    conn.commit()
    conn.close()
    send_email(settings.NOTIFY_EMAIL, f"Nueva reserva para {fecha}", f"{nombre} ha reservado un {tipo_evento} para el {fecha}. Email: {email}")
    return {"success": True, "message": "Reserva registrada y notificada."}

def get_availability(fecha):
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM calendario WHERE fecha=?", (fecha,))
    count = c.fetchone()[0]
    conn.close()
    # Aquí puedes personalizar el límite de eventos por día
    if count == 0:
        return "Disponible"
    else:
        return f"Ya hay {count} evento(s) ese día. Consulta disponibilidad específica."

init_db()
