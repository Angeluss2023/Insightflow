import axios from 'axios';

const baseUrl = 'http://127.0.0.1:5000'; // URL del servidor Flask

/**
 * Ejecuta la extracción de comentarios de TikTok llamando al servidor.
 * @returns {Promise<any>}
 */
export const ejecutarExtraccion = async () => {
  try {
    const response = await axios.post(`${baseUrl}/ejecutar_extraccion`, {});
    return response.data;
  } catch (error) {
    console.error('Error ejecutando extracción:', error);
    throw error;
  }
};

/**
 * Obtiene los comentarios almacenados en el servidor.
 * @returns {Promise<any>}
 */
export const getComentarios = async () => {
  try {
    const response = await axios.get(`${baseUrl}/obtener_datos_tiktok`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo comentarios:', error);
    throw error;
  }
};

/**
 * Analiza los comentarios proporcionados llamando al servidor.
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
