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

# Redirige la raíz a /chat-ui
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/chat-ui")

@app.post("/chat")
async def chat(user_input: dict):
    user_message = user_input.get("message", "")
    lang = user_input.get("lang", "es")
    history = user_input.get("history", None)
    data = chat_with_agent(user_message, lang, history)
    return data

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

# Interfaz web: reservas propuestas desde el chat
from fastapi import Request, Form
from fastapi.responses import RedirectResponse

@app.get("/reservas", response_class=HTMLResponse)
async def reservas_page(request: Request):
    # Muestra las propuestas pendientes y su estado
    eventos_confirmados = [
        {
            "title": f"{r['servicio']} - {r['lugar']}",
            "start": r["dia"],
            "extendedProps": {
                "nombre": r["servicio"],
                "lugar": r["lugar"],
                "precio": r["precio"]
            }
        }
        for r in temp_reservas if r.get("estado") == "confirmada"
    ]
    return templates.TemplateResponse(
        "reservas.html",
        {"request": request, "propuestas": temp_reservas, "eventos_confirmados": eventos_confirmados}
    )

@app.post("/reservas/accion")
async def reservas_accion(idx: int = Form(...), accion: str = Form(...)):
    # Cambia estado de la propuesta
    if 0 <= idx < len(temp_reservas):
        temp_reservas[idx]["estado"] = accion
    return RedirectResponse("/reservas", status_code=303)


# Interfaz web: chat con el agente
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# --- API para reservas desde el chat ---
from fastapi import Body
from fastapi.responses import JSONResponse

# Variable temporal para demo
temp_reservas = []

@app.post("/api/reserva")
async def api_reserva(data: dict = Body(...)):
    # Guardar en memoria (puedes cambiar por DB)
    temp_reservas.append(data)
    print("[Reserva recibida]", data)
    return {"ok": True}



