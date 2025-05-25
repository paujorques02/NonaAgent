from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.agent import chat_with_agent
from app.calendar import create_reservation, get_availability, get_services
from app.config import settings
from twilio.twiml.messaging_response import MessagingResponse
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.post("/chat")
async def chat(user_input: dict):
    user_message = user_input.get("message", "")
    lang = user_input.get("lang", "es")
    history = user_input.get("history", None)
    response = chat_with_agent(user_message, lang, history)
    return {"response": response}

@app.post("/translate")
async def translate(payload: dict):
    messages = payload.get("messages", [])  # [{"text":..., "who":...}]
    source_lang = payload.get("source_lang", "es")
    target_lang = payload.get("target_lang", "en")
    from app.agent import translate_messages
    translated = translate_messages(messages, source_lang, target_lang)
    return {"messages": translated}

@app.post("/reserva")
async def reserva_endpoint(request: Request):
    data = await request.json()
    fecha = data.get("fecha")
    tipo_evento = data.get("tipo_evento")
    nombre = data.get("nombre")
    email = data.get("email")
    reserva = create_reservation(fecha, tipo_evento, nombre, email)
    return reserva

@app.get("/disponibilidad")
async def disponibilidad_endpoint(fecha: str):
    disponibilidad = get_availability(fecha)
    return {"disponibilidad": disponibilidad}

# WhatsApp Webhook (Twilio)
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    user_message = form.get("Body", "")
    response_text = chat_with_agent(user_message)
    twilio_resp = MessagingResponse()
    twilio_resp.message(response_text)
    return HTMLResponse(content=str(twilio_resp), media_type="application/xml")

# Interfaz web: servicios
@app.get("/servicios", response_class=HTMLResponse)
async def servicios_page(request: Request):
    servicios = get_services()
    return templates.TemplateResponse("servicios.html", {"request": request, "servicios": servicios})

# Interfaz web: calendario/reservas (simple)
@app.get("/reservas", response_class=HTMLResponse)
async def reservas_page(request: Request):
    # Para demo: muestra reservas simples
    import sqlite3
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute('SELECT fecha, tipo_evento, nombre, email FROM calendario ORDER BY fecha DESC')
    reservas = c.fetchall()
    conn.close()
    return templates.TemplateResponse("reservas.html", {"request": request, "reservas": reservas})

# Interfaz web: chat con el agente
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
