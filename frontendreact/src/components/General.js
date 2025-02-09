import React, { useState } from 'react';
import { procesarDatosGenerales } from '../services/generalService';

function General() {
  const [datosGenerales, setDatosGenerales] = useState(null);
  const [error, setError] = useState(null);

  const handleProcesarDatos = async () => {
    try {
      const datos = await procesarDatosGenerales();
      setDatosGenerales(datos);
    } catch (err) {
      console.error(err);
      setError('Error al procesar datos generales');
    }
  };

  return (
    <div>
      <h1>Gestión de Datos Generales</h1>
      <button onClick={handleProcesarDatos}>Procesar Datos Generales</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {datosGenerales && (
        <div>
          <h2>Datos Generales Procesados:</h2>
          <pre>{JSON.stringify(datosGenerales, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default General;
