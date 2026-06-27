import asyncio
import urllib.parse

from playwright.async_api import async_playwright, TimeoutError

# ✅ User-agent de un navegador real para evitar bloqueos
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

async def buscar_walmart(query: str, max_resultados: int = 5, reintentos: int = 3):
    """
    Busca productos en Walmart CR con reintentos automáticos.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for intento in range(1, reintentos + 1):
            page = await browser.new_page(user_agent=USER_AGENT)

            try:
                encoded_query = urllib.parse.quote(query)
                url = f"https://www.walmart.co.cr/search?query={encoded_query}"

                print(f"🔄 Intento {intento}/{reintentos} — {url}")

                # ✅ networkidle espera a que la página termine de cargar datos dinámicos
                await page.goto(url, wait_until="networkidle", timeout=60000)

                # ✅ Espera el selector de productos
                await page.wait_for_selector(
                    'article.vtex-product-summary-2-x-element',
                    timeout=25000
                )

                products = await page.query_selector_all('article.vtex-product-summary-2-x-element')

                resultados = []
                for product in products[:max_resultados]:
                    try:
                        name_el = await product.query_selector('span#product-summary-sku-name')
                        name = await name_el.inner_text() if name_el else "No encontrado"

                        price_el = await product.query_selector(
                            'div.vtex-store-components-3-x-sellingPrice '
                            'span.vtex-store-components-3-x-currencyContainer span'
                        )
                        price = await price_el.inner_text() if price_el else "No encontrado"

                        url_el = await product.query_selector('a[href*="/p"]')
                        product_url = (
                            "https://www.walmart.co.cr" + await url_el.get_attribute('href')
                            if url_el else "No encontrado"
                        )

                        resultados.append({
                            "descripcion": name.strip(),
                            "precio": price.strip(),
                            "url": product_url
                        })

                    except Exception as e:
                        print(f"⚠️ Error procesando producto: {e}")
                        continue

                await page.close()
                await browser.close()

                if resultados:
                    return {"tienda": "Walmart", "productos": resultados, "mensaje": None}
                else:
                    return {"tienda": "Walmart", "productos": [], "mensaje": "No se encontraron productos para esta búsqueda."}

            except TimeoutError:
                print(f"⏱️ Timeout en intento {intento}/{reintentos}")
                await page.close()

                if intento < reintentos:
                    # ✅ Espera 2 segundos antes de reintentar
                    await asyncio.sleep(2)
                else:
                    await browser.close()
                    return {
                        "tienda": "Walmart",
                        "productos": [],
                        "mensaje": f"Timeout después de {reintentos} intentos. La página no respondió."
                    }

            except Exception as e:
                await page.close()
                await browser.close()
                return {"tienda": "Walmart", "productos": [], "mensaje": f"Error inesperado: {str(e)}"}


# ---------------- Main para prueba ----------------
async def main():
    producto = input("🔎 Ingresa el producto a buscar en Walmart: ")
    max_resultados = input("🔹 Número máximo de resultados (por defecto 5): ")

    try:
        max_resultados = int(max_resultados)
    except ValueError:
        max_resultados = 5

    resultados = await buscar_walmart(producto, max_resultados)

    print("\n===== Resultados =====")
    if resultados["productos"]:
        for idx, prod in enumerate(resultados["productos"], start=1):
            print(f"{idx}. {prod['descripcion']}")
            print(f"   Precio: {prod['precio']}")
            print(f"   URL: {prod['url']}")
    else:
        print(resultados["mensaje"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")