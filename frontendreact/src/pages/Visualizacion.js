import React, { useEffect, useState } from "react";
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Alert,
  Divider,
} from "@mui/material";
import { SiTiktok } from "react-icons/si"; // Importa el ícono de TikTok
import { YouTube, Language } from "@mui/icons-material";
import { obtenerDatos } from "../services/backendService";

function Visualizacion() {
  const [data, setData] = useState({ tiktok: [], youtube: [], web: [] });
  const [images, setImages] = useState({ tiktok: [], youtube: [], web: [] });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const platforms = ["tiktok", "youtube", "web"];
        const results = await Promise.all(
          platforms.map((platform) => obtenerDatos(platform))
        );

        const newData = { tiktok: [], youtube: [], web: [] };
        const newImages = { tiktok: [], youtube: [], web: [] };

        platforms.forEach((platform, index) => {
          newData[platform] = results[index].data;
          newImages[platform] = results[index].files.images;
        });

        setData(newData);
        setImages(newImages);
      } catch (err) {
        setError("Error obteniendo los datos.");
      }
    };

    fetchData();
  }, []);

  const renderDataSection = (platform, color, Icon) => (
    <Card sx={{ borderLeft: `4px solid ${color}`, margin: "16px" }}>
      <CardContent>
        <Typography
          variant="h6"
          sx={{ display: "flex", alignItems: "center", color: color }}
        >
          <Icon style={{ marginRight: "8px" }} /> Datos de {platform.toUpperCase()}
        </Typography>
        <Divider sx={{ marginY: "8px" }} />

        <Typography variant="body1" sx={{ marginTop: "16px" }}>
          Comentarios Extraídos:
        </Typography>
        <Box
          sx={{
            maxHeight: "200px",
            overflowY: "auto",
            backgroundColor: "#f7f7f7",
            padding: "8px",
            borderRadius: "8px",
            marginBottom: "16px",
          }}
        >
          {data[platform].length > 0 ? (
            data[platform].map((comment, index) => (
              <Typography key={index} variant="body2" sx={{ marginBottom: "4px" }}>
                {comment.comment}
              </Typography>
            ))
          ) : (
            <Typography variant="body2" color="text.secondary">
              No hay comentarios disponibles.
            </Typography>
          )}
        </Box>

        <Typography variant="body1" sx={{ marginTop: "16px" }}>
          Visualizaciones Generadas:
        </Typography>
        <Grid container spacing={2} sx={{ marginTop: "16px" }}>
          {images[platform].map((image, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                sx={{
                  boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                  borderRadius: "8px",
                }}
              >
                <CardContent>
                  <img
                    src={image}
                    alt={`Gráfico ${index}`}
                    style={{ width: "100%", borderRadius: "8px" }}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ padding: "16px" }}>
      <Typography
        variant="h4"
        align="center"
        gutterBottom
        sx={{ fontWeight: "bold", color: "#1976D2" }}
      >
        Visualización de Datos Extraídos
      </Typography>
      <Typography
        variant="body1"
        align="center"
        sx={{ marginBottom: "24px", color: "#757575" }}
      >
        Aquí puedes ver los datos extraídos y visualizaciones de las plataformas seleccionadas.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ margin: "16px", backgroundColor: "#ffebee", color: "#b71c1c" }}>
          {error}
        </Alert>
      )}

      {renderDataSection("tiktok", "#2196F3", SiTiktok)}
      {renderDataSection("youtube", "#FF0000", YouTube)}
      {renderDataSection("web", "#2196F3", Language)}
    </Box>
  );
}

export default Visualizacion;
