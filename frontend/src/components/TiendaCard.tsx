// src/components/TiendaCard.tsx

import React from "react";

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

interface TiendaCardProps {
  tiendaData: Tienda;
}

const TiendaCard: React.FC<TiendaCardProps> = ({ tiendaData }) => {
  const count = tiendaData.productos?.length ?? 0;
  const mensajeBruto = tiendaData.mensaje?.trim();
  const esTecnico = /timeout|error|page\.goto|exceeded|call log/i.test(
    mensajeBruto ?? "",
  );
  const mensajeAMostrar = mensajeBruto
    ? esTecnico
      ? `No se encontraron productos en ${tiendaData.tienda}.`
      : mensajeBruto
    : "No se encontraron productos.";

  return (
    <div className="tienda-card">
      <div className="tienda-header">
        <h2>🏪 {tiendaData.tienda}</h2>
        {count > 0 && <span className="tienda-badge">{count} productos</span>}
      </div>

      {count > 0 ? (
        <ul className="productos-lista">
          {tiendaData.productos.map((producto, index) => (
            <li key={index} className="producto-item">
              <a
                href={
                  producto.url !== "No encontrado" ? producto.url : undefined
                }
                target="_blank"
                rel="noopener noreferrer"
                className="producto-descripcion"
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  cursor:
                    producto.url !== "No encontrado" ? "pointer" : "default",
                }}
                title={producto.url !== "No encontrado" ? "Ver en tienda" : ""}
              >
                {producto.descripcion}
              </a>
              <span className="producto-precio">{producto.precio}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-encontrado">{mensajeAMostrar}</p>
      )}
    </div>
  );
};

export default TiendaCard;
