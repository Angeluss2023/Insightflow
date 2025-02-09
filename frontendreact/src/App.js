import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import Visualizacion from "./pages/Visualizacion";
import Analisis from "./pages/Analisis";
import { AppBar, Tabs, Tab, Box } from "@mui/material";

function App() {
  const tabs = [
    { label: "Inicio", path: "/" },
    { label: "Visualización", path: "/visualizacion" },
    { label: "Análisis General", path: "/analisis" },
  ];

  return (
    <Router>
      <AppBar position="static" color="default">
        <Tabs centered>
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              component={Link}
              to={tab.path}
            />
          ))}
        </Tabs>
      </AppBar>
      <Box sx={{ p: 2 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/visualizacion" element={<Visualizacion />} />
          <Route path="/analisis" element={<Analisis />} />
        </Routes>
      </Box>
    </Router>
  );
}

export default App;
