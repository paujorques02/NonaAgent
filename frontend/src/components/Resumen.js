import React from 'react';
import './Resumen.css';

const Resumen = ({ resumen }) => {
  return (
    <div className="resumen-box">
      <h4>Resumen</h4>
      <div className="resumen-item"><b>servicio:</b> {resumen.servicio || '...'}</div>
      <div className="resumen-item"><b>lugar:</b> {resumen.lugar || '...'}</div>
      <div className="resumen-item"><b>precio:</b> {resumen.precio || '...'}</div>
      <div className="resumen-item"><b>día:</b> {resumen.dia || '...'}</div>
    </div>
  );
};

export default Resumen;
