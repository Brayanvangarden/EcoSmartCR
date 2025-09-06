import { useState } from "react";

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

// 💡 Función auxiliar para convertir el precio de string a número y poder compararlos
const parsePrice = (priceString: string): number => {
  // Elimina el símbolo de colón y los puntos de miles, y reemplaza la coma decimal con un punto
  const cleanedString = priceString.replace("₡", "").replace(/\./g, "").replace(",", ".");
  return parseFloat(cleanedString);
};

export default function Productos() {
  const [query, setQuery] = useState("");
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const buscarProducto = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setApiResponse(null);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/buscar?query=${query}`
      );

      if (!res.ok) {
        throw new Error("Error al consultar el backend.");
      }

      const data: ApiResponse = await res.json();
      setApiResponse(data);
    } catch (err: any) {
      setError(err.message || "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  // 💡 Lógica para encontrar el precio más bajo y el más alto
  const findCheapestPrice = (): number | null => {
    if (!apiResponse?.productos || apiResponse.productos.length === 0) return null;
    let minPrice = Infinity;
    for (const producto of apiResponse.productos) {
      const parsedPrice = parsePrice(producto.precio);
      if (!isNaN(parsedPrice) && parsedPrice < minPrice) {
        minPrice = parsedPrice;
      }
    }
    return minPrice;
  };

  const cheapestPrice = findCheapestPrice();

  return (
    <div className="w-full max-w-md bg-white p-6 shadow-lg rounded-xl">
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

      {/* Mensajes */}
      {loading && <p className="mt-4 text-center text-blue-600">Cargando...</p>}
      {error && <p className="mt-4 text-center text-red-500 font-medium">{error}</p>}

      {/* Resultado */}
      {(apiResponse?.productos && apiResponse.productos.length > 0) && (
        <div className="mt-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Resultados de {apiResponse.tienda}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {apiResponse.productos.map((producto, index) => {
              const parsedPrice = parsePrice(producto.precio);
              const isCheapest = parsedPrice === cheapestPrice;
              
              return (
                <div 
                  key={index} 
                  className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm transform transition duration-300 hover:shadow-md hover:scale-105"
                >
                  <p className="font-semibold text-gray-800 line-clamp-2">{producto.descripcion}</p>
                  <p className={`text-xl mt-2 ${isCheapest ? 'text-green-600 font-extrabold' : 'text-gray-700 font-bold'}`}>
                    {producto.precio}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {apiResponse?.mensaje && <p className="mt-4 text-center text-gray-500 italic">{apiResponse.mensaje}</p>}
    </div>
  );
}