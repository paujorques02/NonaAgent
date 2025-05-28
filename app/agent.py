# agent.py
import os
from app.calendar import get_services, get_service_price
from dotenv import load_dotenv

# Intenta cargar la API key de Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def buscar_servicios_por_tipo(tipo:str):
    tipo = tipo.lower()
    servicios = get_services()
    resultados = []
    for nombre, descripcion, precio in servicios:
        if tipo in nombre.lower() or tipo in descripcion.lower():
            resultados.append({'nombre': nombre, 'precio': precio})
    return resultados


def chat_with_agent(user_message: str, lang: str = "es", history=None) -> dict:
    msg = user_message.lower()
    # Si hay API key de Gemini, usa el LLM
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            estilos = {
                "es": "Responde como una wedding planner real chateando por WhatsApp: usa frases cortas, tono cálido y cercano, puedes usar emojis, haz preguntas directas, no hagas listas largas, ni hables como una web ni como un blog. Sé natural y espontánea. Responde siempre en español. IMPORTANTE: Cuando devuelvas la fecha del evento (campo 'dia'), SIEMPRE usa el formato internacional ISO: AAAA-MM-DD (por ejemplo, 2025-08-05). No uses palabras ni meses en texto.",
                "en": "Reply as a real wedding planner chatting on WhatsApp: short sentences, warm and close tone, you can use emojis, ask direct questions, don't make long lists, don't talk like a website or a blog. Be natural and spontaneous. Always reply in English.",
                "fr": "Réponds comme une wedding planner réelle sur WhatsApp : phrases courtes, ton chaleureux et proche, tu peux utiliser des emojis, pose des questions directes, pas de longues listes, ne parle pas comme un site web ou un blog. Sois naturelle et spontanée. Réponds toujours en français.",
                "it": "Rispondi come una vera wedding planner che chatta su WhatsApp: frasi brevi, tono caldo e vicino, puoi usare emoji, fai domande dirette, non fare lunghe liste, non parlare come un sito o un blog. Sii naturale e spontanea. Rispondi sempre in italiano."
            }
            estilo = estilos.get(lang, estilos["es"])
            chat_context = ""
            if history:
                chat_context = "\nHistorial reciente:\n" + "\n".join([f"{m['who']}: {m['text']}" for m in history])
            prompt = f"{estilo}\n{chat_context}\n\nAhora, analiza el mensaje del usuario y responde SIEMPRE en formato JSON así: {{'respuesta': <respuesta del asistente>, 'servicio': <servicio detectado o vacío>, 'lugar': <lugar detectado o vacío>, 'precio': <precio detectado o vacío>, 'dia': <día detectado o vacío>}}. Si algún campo no se menciona, déjalo vacío.\n\nMensaje del usuario: {user_message}"
            model = genai.GenerativeModel('gemini-2.0-flash')
            respuesta = model.generate_content(prompt)
            # Limpiar el texto para extraer solo el JSON
            import re
            raw = respuesta.text.strip()
            # Elimina bloques markdown y busca el primer objeto JSON
            raw = re.sub(r'^```json|^```', '', raw, flags=re.IGNORECASE).strip()
            raw = re.sub(r'```$', '', raw).strip()
            # Busca el primer {...} con regex
            match = re.search(r'\{[\s\S]*\}', raw)
            if match:
                json_str = match.group(0)
            else:
                json_str = raw
            try:
                data = json.loads(json_str.replace("'", '"'))
            except Exception as e:
                data = {"respuesta": raw, "servicio": "", "lugar": "", "precio": "", "dia": ""}
            # Asegura todos los campos
            for k in ["respuesta", "servicio", "lugar", "precio", "dia"]:
                if k not in data:
                    data[k] = ""
            return data
        except Exception as e:
            return f"[Error usando Gemini: {e}]"
    # Si no hay API key, devuelve campos vacíos y una respuesta genérica
    return {
        "respuesta": "¡Hola! Soy el asistente de eventos. Puedo informarte sobre servicios, precios, disponibilidad y reservas. ¿En qué puedo ayudarte?",
        "servicio": "",
        "lugar": "",
        "precio": "",
        "dia": ""
    }
