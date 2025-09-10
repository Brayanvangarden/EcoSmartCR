// src/components/TiendaCard.tsx

import React from 'react';

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
    return (
        <div className="tienda-card">
            <h2>{tiendaData.tienda}</h2>
            {tiendaData.productos && tiendaData.productos.length > 0 ? (
                <ul className="productos-lista">
                    {tiendaData.productos.map((producto, index) => (
                        <li key={index} className="producto-item">
                            <p className="producto-descripcion">{producto.descripcion}</p>
                            <p className="producto-precio">{producto.precio}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="no-encontrado">{tiendaData.mensaje || "No se encontraron productos."}</p>
            )}
        </div>
    );
};

export default TiendaCard;