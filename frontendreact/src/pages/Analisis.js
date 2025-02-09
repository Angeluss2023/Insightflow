import React, { useEffect, useState } from "react";
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
  Button,
} from "@mui/material";
import {
  BarChart,
  PieChart,
  Tag,
} from "@mui/icons-material";
import { procesarDatosGenerales } from "../services/backendService";

function AnalisisGeneral() {
  const [data, setData] = useState([]);
  const [images, setImages] = useState({ wordcloud: "", pieChartModelo: "", pieChartTransformers: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleProcesarGenerales = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await procesarDatosGenerales();
      setData(response.data);

      // Base URL del servidor Flask
      const baseUrl = "http://127.0.0.1:5000";

      // Extraer y asignar las URLs de las imágenes
      const wordcloudUrl = response.files.images.find((img) => img.includes("nube_de_palabras.png")) || "";
      const pieChartModeloUrl = response.files.images.find((img) => img.includes("grafico_pastel_modelo.png")) || "";
      const pieChartTransformersUrl = response.files.images.find((img) => img.includes("grafico_pastel_transformers.png")) || "";

      // Guardar las URLs de las imágenes en el estado
      setImages({
        wordcloud: `${baseUrl}/${wordcloudUrl}`,
        pieChartModelo: `${baseUrl}/${pieChartModeloUrl}`,
        pieChartTransformers: `${baseUrl}/${pieChartTransformersUrl}`,
      });
    } catch (err) {
      setError("Error procesando el análisis general.");
      console.error("❌ Error procesando datos generales:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ padding: "16px" }}>
      <Typography
        variant="h4"
        align="center"
        gutterBottom
        sx={{ fontWeight: "bold", color: "#673AB7" }}
      >
        Resultados del Análisis General
      </Typography>
      <Typography
        variant="body1"
        align="center"
        sx={{ marginBottom: "24px", color: "#757575" }}
      >
        Este análisis combina datos de múltiples plataformas para proporcionar una visión integral sobre el nivel de aceptación de la Inteligencia Artificial en la vida cotidiana.
      </Typography>

      <Button
        variant="contained"
        color="secondary"
        onClick={handleProcesarGenerales}
        sx={{ marginBottom: "24px", display: "block", marginLeft: "auto", marginRight: "auto" }}
        disabled={loading}
      >
        {loading ? <CircularProgress size={24} /> : "Procesar Análisis General"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ margin: "16px", backgroundColor: "#ffebee", color: "#b71c1c" }}>
          {error}
        </Alert>
      )}

      {data.length > 0 && (
        <>
          {/* Resumen de Datos */}
          <Typography variant="h6" sx={{ marginTop: "24px", fontWeight: "bold" }}>
            Resumen de Datos Combinados:
          </Typography>
          <Box sx={{ maxHeight: "200px", overflowY: "auto", padding: "8px", borderRadius: "8px", backgroundColor: "#f7f7f7", marginBottom: "24px", border: "1px solid #ccc" }}>
            {data.map((item, index) => (
              <Typography key={index} variant="body2" sx={{ marginBottom: "4px" }}>
                {item.comment}
              </Typography>
            ))}
          </Box>

          {/* Sección de Gráficos */}
          <Typography variant="h6" sx={{ marginTop: "24px", fontWeight: "bold" }}>
            Visualizaciones Generadas:
          </Typography>
          <Grid container spacing={2} sx={{ marginTop: "16px" }}>
            {images.wordcloud && (
              <Grid item xs={12} sm={6} md={4}>
                <Card
                  sx={{
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                    borderRadius: "8px",
                  }}
                >
                  <CardContent>
                    <img
                      src={images.wordcloud}
                      alt="Nube de Palabras"
                      style={{ width: "100%", borderRadius: "8px" }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            )}
            {images.pieChartModelo && (
              <Grid item xs={12} sm={6} md={4}>
                <Card
                  sx={{
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                    borderRadius: "8px",
                  }}
                >
                  <CardContent>
                    <img
                      src={images.pieChartModelo}
                      alt="Gráfico de Pastel Modelo"
                      style={{ width: "100%", borderRadius: "8px" }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            )}
            {images.pieChartTransformers && (
              <Grid item xs={12} sm={6} md={4}>
                <Card
                  sx={{
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                    borderRadius: "8px",
                  }}
                >
                  <CardContent>
                    <img
                      src={images.pieChartTransformers}
                      alt="Gráfico de Pastel Transformers"
                      style={{ width: "100%", borderRadius: "8px" }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          {/* Hallazgos Destacados */}
          <Typography variant="h6" sx={{ marginTop: "24px", fontWeight: "bold" }}>
            Principales Hallazgos:
          </Typography>
          <Grid container spacing={2} sx={{ marginTop: "16px" }}>
            <Grid item xs={12} sm={6} md={4}>
              <Card
                sx={{
                  boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                  borderRadius: "8px",
                  padding: "16px",
                  textAlign: "center",
                }}
              >
                <BarChart sx={{ fontSize: 48, color: "#2196F3" }} />
                <Typography variant="h6" sx={{ marginTop: "8px" }}>
                  Total de Comentarios
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "#2196F3" }}>
                  {data.length}
                </Typography>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card
                sx={{
                  boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                  borderRadius: "8px",
                  padding: "16px",
                  textAlign: "center",
                }}
              >
                <PieChart sx={{ fontSize: 48, color: "#FF5722" }} />
                <Typography variant="h6" sx={{ marginTop: "8px" }}>
                  Gráficos Generados
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "#FF5722" }}>
                  3
                </Typography>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card
                sx={{
                  boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                  borderRadius: "8px",
                  padding: "16px",
                  textAlign: "center",
                }}
              >
                <Tag sx={{ fontSize: 48, color: "#673AB7" }} />
                <Typography variant="h6" sx={{ marginTop: "8px" }}>
                  Palabras Clave
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: "bold", color: "#673AB7" }}>
                  Nube de Palabras
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}

export default AnalisisGeneral;
