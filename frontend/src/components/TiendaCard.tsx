// src/components/TiendaCard.tsx
import React from "react";

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

interface TiendaCardProps {
  data: ApiResponse;
}

const parsePrice = (priceString: string): number => {
  const cleanedString = priceString
    .replace("₡", "")
    .replace(/\./g, "")
    .replace(",", ".");
  return parseFloat(cleanedString);
};

const TiendaCard: React.FC<TiendaCardProps> = ({ data }) => {
  const { tienda, productos, mensaje } = data;

  const findCheapestPrice = (): number | null => {
    if (!productos || productos.length === 0) return null;
    let minPrice = Infinity;
    for (const producto of productos) {
      const parsedPrice = parsePrice(producto.precio);
      if (!isNaN(parsedPrice) && parsedPrice < minPrice) {
        minPrice = parsedPrice;
      }
    }
    return minPrice;
  };

  const cheapestPrice = findCheapestPrice();

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg border border-gray-200">
     <h3 className="text-2xl font-bold text-green-600 mb-6 text-center">
  {tienda}
</h3>
      {mensaje && <p className="text-center text-gray-500 italic">{mensaje}</p>}

      {!mensaje && productos.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {productos.map((producto, index) => {
            const parsedPrice = parsePrice(producto.precio);
            const isCheapest = parsedPrice === cheapestPrice;

            return (
              <a
                key={index}
                href={producto.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-white border border-gray-200 rounded-lg shadow-sm transform transition duration-300 hover:shadow-lg hover:scale-105"
              >
                <p className="font-semibold text-gray-800 line-clamp-2">
                  {producto.descripcion}
                </p>
                <p
                  className={`text-lg mt-2 ${
                    isCheapest
                      ? "text-green-600 font-extrabold"
                      : "text-gray-700 font-bold"
                  }`}
                >
                  {producto.precio}
                </p>
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default TiendaCard;
