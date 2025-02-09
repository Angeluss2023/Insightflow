import React, { useState } from "react";
import { Typography, Box, Button, CircularProgress, Alert } from "@mui/material";
import { ejecutarExtraccion } from "../services/backendService";

function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExtraccion = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await ejecutarExtraccion();
      alert(response.mensaje);
    } catch (err) {
      setError("Error ejecutando la extracción.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ textAlign: "center", mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        ¿Por qué analizar el Nivel de Aceptación de la Inteligencia Artificial?
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        El nivel de aceptación de la Inteligencia Artificial en la vida cotidiana
        es un desafío clave en la adopción de tecnologías emergentes. Este análisis
        busca identificar barreras y mostrar el impacto potencial en áreas como
        educación, salud y negocios.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={handleExtraccion}
        disabled={loading}
      >
        {loading ? <CircularProgress size={24} /> : "Ejecutar Extracción de Datos"}
      </Button>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Box>
  );
}

export default Home;
