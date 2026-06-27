# scraper/pricesmart.py

import asyncio
import urllib.parse
from playwright.async_api import async_playwright, TimeoutError

async def buscar_pricesmart(query: str, max_resultados: int = 5):
    """
    Busca productos en Pricesmart Costa Rica.
    """
    resultados = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            encoded_query = urllib.parse.quote(query)
            url = f"https://www.pricesmart.com/es-cr/busqueda?q={encoded_query}"
            
            await page.goto(url)

            try:
                # 💡 Selector principal para cada tarjeta de producto
                await page.wait_for_selector('div.product-card-vertical', timeout=20000)
            except TimeoutError:
                await browser.close()
                return {"tienda": "Pricesmart", "productos": [], "mensaje": "Timeout: La página tardó demasiado en cargar. No se encontraron resultados."}

            products = await page.query_selector_all('div.product-card-vertical')

            for product in products[:max_resultados]:
                try:
                    # 💡 Selector para el nombre del producto
                    name_el = await product.query_selector('span.product-card__title')
                    name = await name_el.inner_text() if name_el else "No encontrado"

                    # 💡 Selector para el precio
                    price_el = await product.query_selector('div.product-card__price span.sf-price__regular')
                    price = await price_el.inner_text() if price_el else "No encontrado"

                    # 💡 Selector para la URL del producto
                    url_el = await product.query_selector('a.sf-link[href*="/producto/"]')
                    product_url = "https://www.pricesmart.com" + await url_el.get_attribute('href') if url_el else "No encontrado"

                    # Intentar obtener la descripción completa desde la página del producto (h1.sf-heading__title)
                    descripcion_completa = name.strip()
                    if product_url and product_url != "No encontrado":
                        try:
                            product_page = await browser.new_page()
                            await product_page.goto(product_url, timeout=15000)
                            try:
                                await product_page.wait_for_selector('h1.sf-heading__title', timeout=8000)
                                title_el = await product_page.query_selector('h1.sf-heading__title')
                                if title_el:
                                    text = await title_el.inner_text()
                                    if text and text.strip():
                                        descripcion_completa = text.strip()
                            except TimeoutError:
                                # No se encontró el h1 en la página del producto; mantener nombre del card
                                pass
                            await product_page.close()
                        except Exception:
                            # Si falla abrir la página del producto, ignorar y usar el nombre del card
                            try:
                                await product_page.close()
                            except Exception:
                                pass

                    resultados.append({
                        "descripcion": descripcion_completa,
                        "precio": price.strip(),
                        "url": product_url
                    })
                except Exception as e:
                    print(f"Error procesando un producto: {e}")
                    continue

            await browser.close()
            mensaje = None if resultados else "No se encontraron productos."
            return {"tienda": "Pricesmart", "productos": resultados, "mensaje": mensaje}

    except Exception as e:
        return {"tienda": "Pricesmart", "productos": [], "mensaje": f"Error inesperado: {str(e)}"}

# ---------------- Main para prueba ----------------
async def main():
    producto = input("🔎 Ingresa el producto a buscar en Pricesmart: ")
    max_resultados = input("🔹 Número máximo de resultados (por defecto 5): ")

    try:
        max_resultados = int(max_resultados)
    except ValueError:
        max_resultados = 5

    resultados = await buscar_pricesmart(producto, max_resultados)

    print("\n===== Resultados =====")
    if resultados["productos"]:
        for idx, prod in enumerate(resultados["productos"], start=1):
            print(f"{idx}. {prod['descripcion']}")
            print(f"   Precio: {prod['precio']}")
    else:
        print(resultados["mensaje"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")