import React, { useState } from 'react';
import { ejecutarExtraccionWeb, getDatosWeb, analizarComentarios } from '../services/paginaService';

function Pagina() {
  const [datosWeb, setDatosWeb] = useState([]);
  const [resultadoAnalisis, setResultadoAnalisis] = useState(null);
  const [error, setError] = useState(null);

  const handleExtraccionWeb = async () => {
    try {
      await ejecutarExtraccionWeb();
      alert('Extracción de páginas web ejecutada exitosamente');
    } catch (err) {
      console.error(err);
      setError('Error al ejecutar la extracción de páginas web');
    }
  };

  const handleObtenerDatosWeb = async () => {
    try {
      const datos = await getDatosWeb();
      setDatosWeb(datos);
    } catch (err) {
      console.error(err);
      setError('Error al obtener datos de páginas web');
    }
  };

  const handleAnalizarComentarios = async () => {
    try {
      const resultado = await analizarComentarios(datosWeb);
      setResultadoAnalisis(resultado);
    } catch (err) {
      console.error(err);
      setError('Error al analizar comentarios');
    }
  };

  return (
    <div>
      <h1>Gestión de Datos de Páginas Web</h1>
      <button onClick={handleExtraccionWeb}>Ejecutar Extracción Web</button>
      <button onClick={handleObtenerDatosWeb}>Obtener Datos Web</button>
      <button onClick={handleAnalizarComentarios}>Analizar Comentarios</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <h2>Datos de Páginas Web:</h2>
        <ul>
          {datosWeb.map((dato, index) => (
            <li key={index}>{dato}</li>
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

export default Pagina;
