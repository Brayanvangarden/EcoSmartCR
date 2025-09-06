import { useState } from "react";
import TiendaCard from "./TiendaCard";

// 💡 Interfaz actualizada para que coincida con la respuesta de la API
interface Producto {
  descripcion: string;
  precio: string;
  url: string;
}

// 💡 Nueva interfaz para la respuesta completa de la API
interface ApiResponse {
  tienda: string;
  productos: Producto[];
  mensaje: string | null;
}

export default function Productos() {
  const [query, setQuery] = useState("");
  const [apiResponse, setApiResponse] = useState<ApiResponse[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const buscarProducto = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setApiResponse(null);

    try {
      const res = await fetch(`http://127.0.0.1:8000/buscar?query=${query}`);

      if (!res.ok) {
        throw new Error("Error al consultar el backend.");
      }

      const data: ApiResponse[] = await res.json();
      setApiResponse(data);
    } catch (err: any) {
      setError(err.message || "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="w-full max-w-lg mx-auto mb-10">
        <div className="border-b-4 border-green-500 rounded-full w-24 mx-auto mt-4"></div>
      </div>

      {/* 🔍 Card del buscador */}
      <div className="max-w-4xl mx-auto bg-white p-6 shadow-lg rounded-xl mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          🔍 Buscador de Productos
        </h2>

        <div className="flex flex-col sm:flex-row gap-4 items-center mb-6">
          <input
            type="text"
            placeholder="Ej: arroz"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:outline-none transition duration-300 shadow-sm"
          />
          <button
            onClick={buscarProducto}
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2 font-semibold text-white rounded-full bg-green-600 hover:bg-green-700 transition duration-300 transform hover:scale-105 disabled:bg-gray-400 disabled:transform-none disabled:cursor-not-allowed"
          >
            {loading ? "Buscando..." : "Buscar"}
          </button>
        </div>

        {loading && (
          <p className="mt-4 text-center text-blue-600">Cargando...</p>
        )}
        {error && (
          <p className="mt-4 text-center text-red-500 font-medium">{error}</p>
        )}
      </div>

      {/* 🛒 Cards de resultados (tiendas) */}
      {apiResponse && (
        <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {apiResponse.map((tiendaData, index) => (
            <TiendaCard key={index} data={tiendaData} />
          ))}
        </div>
      )}

      {apiResponse?.every((d) => !d.productos?.length) && !loading && (
        <p className="mt-4 text-center text-gray-500 italic">
          No se encontraron productos en ninguna tienda.
        </p>
      )}
    </div>
  );
}
