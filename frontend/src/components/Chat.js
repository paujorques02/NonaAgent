import React, { useState } from 'react';
import './Chat.css';

// Expresiones regulares para detectar datos clave
const patrones = {
  servicio: /servicio\s*:?\s*(\w+)/i,
  lugar: /lugar\s*:?\s*([\w\s]+)/i,
  precio: /precio\s*:?\s*([\d,.€]+)/i,
  dia: /d[ií]a\s*:?\s*([\w\s\/-]+)/i
};

const Chat = ({ actualizarResumen }) => {
  const [messages, setMessages] = useState([
    { sender: 'agente', text: '¡Hola! ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { sender: 'usuario', text: input };
    setMessages([...messages, userMsg]);
    extraerDatosClave(input);
    setInput('');
    // Aquí puedes integrar la lógica para enviar el mensaje al backend/IA si lo deseas
  };

  // Extrae datos clave del mensaje del usuario y actualiza el resumen
  const extraerDatosClave = (texto) => {
    let nuevosDatos = {};
    Object.entries(patrones).forEach(([campo, regex]) => {
      const match = texto.match(regex);
      if (match && match[1]) {
        nuevosDatos[campo] = match[1].trim();
      }
    });
    if (Object.keys(nuevosDatos).length > 0) {
      actualizarResumen(nuevosDatos);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">Chat con el agente</div>
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-msg ${msg.sender}`}>{msg.text}</div>
        ))}
      </div>
      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Escribe tu mensaje..."
        />
        <button type="submit">Enviar</button>
      </form>
    </div>
  );
};

export default Chat;
