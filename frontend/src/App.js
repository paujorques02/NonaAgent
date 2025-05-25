import React, { useState } from 'react';
import './App.css';
import Chat from './components/Chat';
import Resumen from './components/Resumen';

function App() {
  // Estado del resumen con los campos clave
  const [resumen, setResumen] = useState({
    servicio: '',
    lugar: '',
    precio: '',
    dia: ''
  });

  // Función para actualizar el resumen desde el chat
  const actualizarResumen = (nuevoResumen) => {
    setResumen(prev => ({ ...prev, ...nuevoResumen }));
  };

  return (
    <div className="main-layout">
      <div className="left-panel">
        <Chat actualizarResumen={actualizarResumen} />
      </div>
      <div className="right-panel">
        <Resumen resumen={resumen} />
      </div>
    </div>
  );
}

export default App;
