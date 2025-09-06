// Productos.tsx

import { useState } from "react";

interface Producto {
  nombre: string;
  precio: number;
}

export default function Productos() {
  const [query, setQuery] = useState("");
  const [resultado, setResultado] = useState<Producto | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const buscarProducto = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResultado(null);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/buscar?producto=${query}`
      );
      if (!res.ok) throw new Error("Error al consultar el backend");

      const data = await res.json();
      setResultado(data);
    } catch (err: any) {
      setError(err.message || "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-white p-6">
      <h2 className="text-xl font-semibold text-gray-700 mb-4">
        🔍 Buscar producto
      </h2>

      {/* Agregamos una clase para centrar el contenedor del input y el botón */}
      <div className="flex flex-col sm:flex-row gap-4 items-center">
        <input
          type="text"
          placeholder="Ej: arroz"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:outline-none transition duration-300"
        />
        <button
          onClick={buscarProducto}
          className="w-full sm:w-auto px-6 py-2 font-semibold text-white rounded-full bg-green-600 hover:bg-green-700 transition duration-300 transform hover:scale-105"
        >
          Buscar
        </button>
      </div>

      {/* Mensajes */}
      {loading && <p className="mt-4 text-center text-blue-600">Cargando...</p>}
      {error && <p className="mt-4 text-center text-red-500">{error}</p>}

      {/* Resultado */}
      {resultado && (
        <div className="mt-6 p-4 border rounded-xl bg-green-50 shadow-sm">
          <h3 className="text-lg font-bold text-green-800">Resultado</h3>
          <p className="text-gray-700 mt-2">
            <span className="font-semibold">{resultado.nombre}</span>
            <br />
            <span className="text-green-700 text-lg">
              ₡{resultado.precio.toLocaleString()}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}