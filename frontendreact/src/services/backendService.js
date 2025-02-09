import axios from 'axios';

const baseUrl = 'http://127.0.0.1:5000';

// Ejecutar extracción
export const ejecutarExtraccion = async () => {
  try {
    const response = await axios.post(`${baseUrl}/ejecutar_extraccion`);
    return response.data;
  } catch (error) {
    console.error('Error ejecutando extracción:', error);
    throw error;
  }
};

// Obtener datos de una plataforma (TikTok, YouTube o Web)
export const obtenerDatos = async (platform) => {
  try {
    const response = await axios.get(`${baseUrl}/obtener_datos/${platform}`);
    return response.data;
  } catch (error) {
    console.error(`Error obteniendo datos de ${platform}:`, error);
    throw error;
  }
};

// Procesar datos generales
export const procesarDatosGenerales = async () => {
  try {
    const response = await axios.get(`${baseUrl}/procesar_datos_generales`);
    return response.data;
  } catch (error) {
    console.error('Error procesando datos generales:', error);
    throw error;
  }
};
