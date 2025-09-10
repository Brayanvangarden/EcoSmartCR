// src/components/Productos.tsx

import React from 'react';
import TiendaCard from './TiendaCard';

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

interface ProductosProps {
    resultados: Tienda[];
}

const Productos: React.FC<ProductosProps> = ({ resultados }) => {
    return (
        <div className="productos-container">
            {resultados.map((tiendaData, index) => (
                <TiendaCard key={index} tiendaData={tiendaData} />
            ))}
        </div>
    );
};

export default Productos;