import axios from 'axios';

const baseUrl = 'http://127.0.0.1:5000'; // Cambia esta URL si tu servidor Flask está en otro lugar

/**
 * Procesa los datos generales llamando al servidor.
 * @returns {Promise<any>}
 */
export const procesarDatosGenerales = async () => {
  try {
    const response = await axios.get(`${baseUrl}/procesar_datos_generales`);
    return response.data;
  } catch (error) {
    console.error('Error procesando datos generales:', error);
    throw error;
  }
};
