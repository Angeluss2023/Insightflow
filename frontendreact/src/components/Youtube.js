import React, { useState } from 'react';
import { ejecutarExtraccion, getComentarios, analizarComentarios } from '../services/youtubeService';

function Youtube() {
  const [comentarios, setComentarios] = useState([]);
  const [resultadoAnalisis, setResultadoAnalisis] = useState(null);
  const [error, setError] = useState(null);

  const handleExtraccion = async () => {
    try {
      await ejecutarExtraccion();
      alert('Extracción ejecutada exitosamente');
    } catch (err) {
      console.error(err);
      setError('Error al ejecutar la extracción');
    }
  };

  const handleObtenerComentarios = async () => {
    try {
      const datos = await getComentarios();
      setComentarios(datos);
    } catch (err) {
      console.error(err);
      setError('Error al obtener comentarios');
    }
  };

  const handleAnalizarComentarios = async () => {
    try {
      const resultado = await analizarComentarios(comentarios);
      setResultadoAnalisis(resultado);
    } catch (err) {
      console.error(err);
      setError('Error al analizar comentarios');
    }
  };

  return (
    <div>
      <h1>Gestión de Comentarios de YouTube</h1>
      <button onClick={handleExtraccion}>Ejecutar Extracción</button>
      <button onClick={handleObtenerComentarios}>Obtener Comentarios</button>
      <button onClick={handleAnalizarComentarios}>Analizar Comentarios</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <h2>Comentarios:</h2>
        <ul>
          {comentarios.map((comentario, index) => (
            <li key={index}>{comentario}</li>
          ))}
        </ul>
      </div>
      {resultadoAnalisis && (
        <div>
          <h2>Resultado del Análisis:</h2>
          <pre>{JSON.stringify(resultadoAnalisis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Youtube;
