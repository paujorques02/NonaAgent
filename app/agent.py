# agent.py
import os
from app.calendar import get_services, get_service_price
from dotenv import load_dotenv

# Intenta cargar la API key de Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_comuniones_context():
    servicios = get_services()
    contexto = ""
    for nombre, descripcion, precio in servicios:
        if "comunión" in nombre.lower() or "comunion" in nombre.lower():
            contexto += f"Servicio: {nombre}\nDescripción: {descripcion}\nPrecio: {precio}€\n\n"
    return contexto.strip()


def chat_with_agent(user_message: str, lang: str = "es", history=None) -> str:
    msg = user_message.lower()
    # Si hay API key de Gemini, usa el LLM
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            estilos = {
                "es": "Responde como una wedding planner real chateando por WhatsApp: usa frases cortas, tono cálido y cercano, puedes usar emojis, haz preguntas directas, no hagas listas largas, ni hables como una web ni como un blog. Sé natural y espontánea. Responde siempre en español.",
                "en": "Reply as a real wedding planner chatting on WhatsApp: use short sentences, warm and friendly tone, you can use emojis, ask direct questions, don't make long lists, don't sound like a website or blog. Be natural and spontaneous. Always reply in English.",
                "fr": "Réponds comme une vraie wedding planner qui discute sur WhatsApp : utilise des phrases courtes, un ton chaleureux et amical, tu peux utiliser des emojis, pose des questions directes, n'écris pas de longues listes, ne parle pas comme un site web ou un blog. Sois naturelle et spontanée. Réponds toujours en français.",
                "it": "Rispondi come una vera wedding planner che chatta su WhatsApp: usa frasi brevi, tono caldo e amichevole, puoi usare emoji, fai domande dirette, non fare elenchi lunghi, non parlare come un sito web o un blog. Sii naturale e spontanea. Rispondi sempre in italiano."
            }
            estilo = estilos.get(lang, estilos["es"])
            # Construir contexto conversacional
            chat_context = ""
            if history and isinstance(history, list):
                # Limita a los últimos 10 mensajes
                for h in history[-10:]:
                    if h.get('who') == 'user':
                        chat_context += (f"Usuario: {h.get('text')}\n")
                    else:
                        chat_context += (f"Wedding Planner: {h.get('text')}\n")
            # Añade el mensaje actual
            chat_context += f"Usuario: {user_message}\nWedding Planner:"
            # Añade contexto de comuniones si aplica
            if "comunión" in msg or "comunion" in msg or (lang=="en" and "communion" in msg) or (lang=="fr" and "communion" in msg) or (lang=="it" and "comunione" in msg):
                contexto = get_comuniones_context()
                prompt = f"{estilo}\nEstos son los precios y servicios de comuniones que puedes usar en tu respuesta:\n{contexto}\n{chat_context}"
            else:
                prompt = f"{estilo}\n{chat_context}"
            model = genai.GenerativeModel('gemini-2.0-flash')
            respuesta = model.generate_content(prompt)
            return respuesta.text.strip()
        except Exception as e:
            return f"[Error usando Gemini: {e}]"
    # Si no hay API key, usa el comportamiento clásico
    # Respuestas sobre servicios
    if any(word in msg for word in ["servicio", "ofreces", "puedes hacer", "qué haces"]):
        servicios = get_services()
        lista = "\n".join([f"- {nombre} ({precio}€)" for nombre, _, precio in servicios])
        return f"Ofrecemos estos servicios:\n{lista}\n¿Te interesa alguno?"
    # Respuestas sobre precios
    elif "precio" in msg or "cuánto cuesta" in msg:
        servicios = get_services()
        lista = "\n".join([f"{nombre}: {precio}€" for nombre, _, precio in servicios])
        return f"Estos son nuestros precios:\n{lista}\n¿Quieres información de algún servicio en concreto?"
    # Respuestas sobre disponibilidad
    elif "disponible" in msg or "disponibilidad" in msg:
        return "¿Para qué fecha necesitas saber la disponibilidad? Por favor, dime la fecha (por ejemplo: 15/07/2025)."
    # Respuestas sobre reservas
    elif "reserva" in msg or "reservar" in msg:
        return "¡Perfecto! Para reservar, dime el tipo de evento, la fecha y tu nombre."
    # Respuesta para tipo de evento
    elif any(evento in msg for evento in ["boda", "bautizo", "comunión", "cumpleaños", "wedding planner"]):
        precio = get_service_price(user_message.title())
        if precio:
            return f"El precio de {user_message.title()} es {precio}€. ¿Quieres reservar o saber disponibilidad?"
        else:
            return f"¡Genial! ¿Para qué fecha te gustaría este servicio?"
    # Respuesta genérica
    else:
        return "¡Hola! Soy el asistente de eventos. Puedo informarte sobre servicios, precios, disponibilidad y reservas. ¿En qué puedo ayudarte?"
