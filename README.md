# Agente de IA para gestión de eventos

## ¿Qué hace?
- Responde a clientes sobre servicios, precios y disponibilidad
- Permite reservar fechas para eventos
- Envía notificaciones por email a la empresa

## ¿Cómo se usa?
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura los datos de correo y base de datos en `app/config.py` o usando variables de entorno.
3. Ejecuta la API:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Usa los endpoints `/chat`, `/reserva` y `/disponibilidad` para interactuar.

## Personalización
- Mejora las respuestas en `app/agent.py`
- Ajusta el calendario en `app/calendar.py`
- Cambia el email de notificación en `app/config.py`
