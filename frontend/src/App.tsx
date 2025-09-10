// src/App.tsx

import React, { useState } from "react";
import axios from "axios";
import Productos from "./components/Productos";
import "./App.css"; // Asegúrate de importar los estilos

interface Producto {
  descripcion: string;
  precio: string;
  url: string;
}

interface Tienda {
  tienda: string;
  productos: Producto[];
  mensaje?: string;
}

const App: React.FC = () => {
  const [query, setQuery] = useState<string>("");
  const [resultados, setResultados] = useState<Tienda[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResultados([]); // Limpiar resultados anteriores

    try {
      const response = await axios.get<Tienda[]>(
        `http://localhost:8000/buscar?query=${query}`
      );
      setResultados(response.data);
    } catch (err) {
      console.error(err);
      setError("Hubo un error al buscar los productos. Inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1> EcoSmart </h1>
        <p>Buscador de Productos</p>
        <form onSubmit={handleSearch} className="search-bar">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="cerveza"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Buscando..." : "Buscar"}
          </button>
        </form>
      </header>

      <main>
        {loading && <p>Cargando resultados...</p>}
        {error && <p className="error-message">{error}</p>}
        {!loading && !error && resultados.length > 0 && (
          <Productos resultados={resultados} />
        )}
        {!loading && !error && resultados.length === 0 && query && (
          <p>No se encontraron resultados para "{query}".</p>
        )}
      </main>
    </div>
  );
};

export default App;
