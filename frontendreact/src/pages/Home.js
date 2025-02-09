import React, { useState } from "react";
import {
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Collapse,
  IconButton,
  Alert,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { ejecutarExtraccion } from "../services/backendService";

function Home() {
  const [expanded, setExpanded] = useState(false);
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

  const toggleExpand = () => {
    setExpanded((prev) => !prev);
  };

  return (
    <Box sx={{ minHeight: "100vh", background: "linear-gradient(to right, #6dd5ed, #2193b0)", py: 8, px: 3 }}>
      {/* Hero Banner */}
      <Box
        sx={{
          textAlign: "center",
          color: "#fff",
          mb: 6,
        }}
      >
        <Typography variant="h2" gutterBottom>
          ¿Por qué analizar el Nivel de Aceptación de la Inteligencia Artificial?
        </Typography>
        <Typography variant="h6" sx={{ maxWidth: "800px", mx: "auto" }}>
          Este análisis identifica barreras en la adopción de tecnologías emergentes como la Inteligencia Artificial y su impacto en la educación, salud y negocios. Nuestro objetivo es ayudar a entender mejor estas tecnologías y su relevancia en la vida cotidiana.
        </Typography>
      </Box>

      {/* Tarjeta Expandible */}
      <Card
        sx={{
          maxWidth: "800px",
          mx: "auto",
          backgroundColor: "#ffffffee",
          boxShadow: "0px 4px 20px rgba(0,0,0,0.2)",
          borderRadius: "16px",
        }}
      >
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Más detalles sobre el problema
          </Typography>
          <Typography variant="body2">
            A pesar de los beneficios de la Inteligencia Artificial, como la automatización y la toma de decisiones, muchas personas todavía tienen preocupaciones sobre su uso. Este proyecto busca abordar estas barreras proporcionando datos y visualizaciones prácticas que demuestren el impacto positivo de la IA en sectores clave.
          </Typography>
        </CardContent>
        <CardActions disableSpacing>
          <Button
            size="small"
            onClick={toggleExpand}
            startIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          >
            {expanded ? "Ver menos" : "Leer más"}
          </Button>
        </CardActions>
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent>
            <Typography variant="body2">
              Con este análisis, esperamos generar conciencia sobre la importancia de adoptar tecnologías emergentes y superar las barreras de desconfianza y desconocimiento. Además, buscamos identificar patrones que puedan ayudar a los desarrolladores y empresas a mejorar sus estrategias de implementación.
            </Typography>
          </CardContent>
        </Collapse>
      </Card>

      {/* Botón de Extracción */}
      <Box sx={{ textAlign: "center", mt: 6 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleExtraccion}
          disabled={loading}
          sx={{
            fontSize: "18px",
            padding: "10px 20px",
            borderRadius: "30px",
            backgroundColor: "#0044cc",
            "&:hover": { backgroundColor: "#003399" },
          }}
        >
          {loading ? "Extrayendo Datos..." : "Ejecutar Extracción de Datos"}
        </Button>
      </Box>

      {/* Mensaje de Error */}
      {error && (
        <Alert severity="error" sx={{ mt: 3, maxWidth: "800px", mx: "auto" }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}

export default Home;
