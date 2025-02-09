import React, { useState } from "react";
import { Typography, Box, Grid, Card, CardContent, Alert } from "@mui/material";
import { obtenerDatos } from "../services/backendService";

function Extraccion() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  const handleObtenerDatos = async (platform) => {
    setError(null);
    try {
      const response = await obtenerDatos(platform);
      setData(response.data);
    } catch (err) {
      setError(`Error obteniendo los datos de ${platform}.`);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Datos Extraídos por Plataforma
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Box sx={{ mt: 2 }}>
        {data.length > 0 ? (
          <Grid container spacing={2}>
            {data.map((item, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card>
                  <CardContent>
                    <Typography>{item.comment}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography>No hay datos disponibles.</Typography>
        )}
      </Box>
    </Box>
  );
}

export default Extraccion;
