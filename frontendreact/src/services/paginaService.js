import axios from 'axios';

const baseUrl = 'http://127.0.0.1:5000'; // Cambia esta URL si tu servidor Flask está en otro lugar

/**
 * Ejecuta la extracción de datos de páginas web.
 * @returns {Promise<any>}
 */
export const ejecutarExtraccionWeb = async () => {
  try {
    const response = await axios.post(`${baseUrl}/ejecutar_extraccion_web`, {});
    return response.data;
  } catch (error) {
    console.error('Error ejecutando extracción de páginas web:', error);
    throw error;
  }
};

/**
 * Obtiene los datos procesados de páginas web.
 * @returns {Promise<any[]>}
 */
export const getDatosWeb = async () => {
  try {
    const response = await axios.get(`${baseUrl}/obtener_datos_web`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo datos de páginas web:', error);
    throw error;
  }
};

/**
 * Analiza los comentarios proporcionados.
 * @param {string[]} comments - Lista de comentarios a analizar.
 * @returns {Promise<any>}
 */
export const analizarComentarios = async (comments) => {
  try {
    const response = await axios.post(`${baseUrl}/analizar_comentarios`, { comments });
    return response.data;
  } catch (error) {
    console.error('Error analizando comentarios:', error);
    throw error;
  }
};
