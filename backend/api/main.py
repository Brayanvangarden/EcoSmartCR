import sys
import os
import asyncio
from fastapi import FastAPI, HTTPException
from multiprocessing import Process, Queue

# Asegúrate de que esta línea esté correcta para tu estructura de carpetas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🔹 Importar la función del scraper
from scraper.scrapers.walmart import buscar_walmart


# Crear la app FastAPI
app = FastAPI(
    title="API Scraper Walmart CR",
    description="API para buscar productos en Walmart Costa Rica usando Playwright y FastAPI",
    version="1.0.0"
)

# 🔹 Endpoint de prueba para verificar que la API responde
@app.get("/ping", summary="Probar conexión")
async def ping():
    """
    Endpoint simple para verificar que la API está funcionando.
    """
    return {"status": "ok"}


def run_scraper(query: str, max_resultados: int, queue: Queue):
    """
    Función que ejecuta el scraper en un proceso separado.
    """
    # 🔹 Es necesario establecer la política de bucle de eventos en cada proceso.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Ejecutar la función de scraping y poner los resultados en la cola
    results = asyncio.run(buscar_walmart(query, max_resultados))
    queue.put(results)


# 🔹 Endpoint principal para scraping en Walmart
@app.get("/buscar", summary="Buscar productos en Walmart CR")
async def buscar_producto(
    query: str, 
    max_resultados: int = 5
):
    """
    Endpoint para buscar productos en Walmart CR.

    **Parámetros:**
    - `query`: nombre del producto a buscar
    - `max_resultados`: cantidad máxima de resultados a retornar (por defecto 5)
    """
    try:
        # Crea una cola para recibir los resultados del proceso
        result_queue = Queue()
        
        # Crea y arranca el proceso para ejecutar el scraper
        scraper_process = Process(target=run_scraper, args=(query, max_resultados, result_queue))
        scraper_process.start()
        
        # Espera hasta 60 segundos por los resultados
        resultados = await asyncio.to_thread(result_queue.get, timeout=60)
        
        # Unirse al proceso para asegurar que termine
        scraper_process.join()
        
        return resultados
    except Exception as e:
        # Captura cualquier excepción y devuelve un error 500
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")