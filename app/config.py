# config.py
import os

class Settings:
    DB_PATH = os.getenv("DB_PATH", "calendario.db")
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "tusuegra@email.com")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "usuario@gmail.com")
    SMTP_PASS = os.getenv("SMTP_PASS", "tu_contraseña")

settings = Settings()
