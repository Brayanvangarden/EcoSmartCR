import asyncio
import json
import urllib.parse

import requests

BASE_URL = "https://www.masxmenos.cr"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

PICK_RUNTIME = (
    "appsEtag,blocks,blocksTree,components,contentMap,extensions,"
    "messages,page,pages,query,queryData,route,runtimeMeta,settings"
)


def construir_url_masxmenos(producto: str) -> str:
    producto = producto.strip()

    encoded_product = urllib.parse.quote(producto, safe="")
    encoded_query = urllib.parse.quote(producto, safe="")
    encoded_runtime = urllib.parse.quote(PICK_RUNTIME, safe="")

    return (
        f"{BASE_URL}/{encoded_product}"
        f"?_q={encoded_query}"
        f"&map=ft"
        f"&__pickRuntime={encoded_runtime}"
    )


def obtener_json_sync(url: str, timeout: int = 60) -> dict:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/plain,*/*",
        "Referer": BASE_URL,
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=timeout,
        allow_redirects=True,
    )

    response.raise_for_status()
    return response.json()


def parsear_data_si_es_string(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def buscar_products_recursivo(value):
    """
    Busca productos en cualquier parte del JSON.
    Soporta:
    - productSearch.products
    - products
    """
    value = parsear_data_si_es_string(value)

    if isinstance(value, dict):
        product_search = value.get("productSearch")

        if isinstance(product_search, dict):
            products = product_search.get("products")

            if isinstance(products, list):
                return products

        direct_products = value.get("products")

        if isinstance(direct_products, list):
            return direct_products

        for child_value in value.values():
            result = buscar_products_recursivo(child_value)

            if result:
                return result

    if isinstance(value, list):
        for item in value:
            result = buscar_products_recursivo(item)

            if result:
                return result

    return []


def extraer_precio(product: dict):
    """
    En VTEX el precio normalmente está en:
    items[0].sellers[0].commertialOffer.Price
    """
    items = product.get("items") or []

    for item in items:
        sellers = item.get("sellers") or []

        for seller in sellers:
            offer = seller.get("commertialOffer") or {}
            price = offer.get("Price")

            if price is not None:
                return price

    return None


def formatear_precio_colones(price):
    if price is None or price == "No encontrado":
        return "No encontrado"

    try:
        return f"¢{float(price):,.2f}"
    except (ValueError, TypeError):
        return "No encontrado"


def normalizar_link(link: str):
    if not link:
        return None

    if link.startswith("http"):
        return link

    return f"{BASE_URL}{link}"


async def buscar_masxmenos(query: str, max_resultados: int = 5, reintentos: int = 3):
    url = construir_url_masxmenos(query)

    for intento in range(1, reintentos + 1):
        try:
            payload = await asyncio.to_thread(obtener_json_sync, url)

            products = buscar_products_recursivo(payload)

            resultados = []

            for product in products[:max_resultados]:
                product_name = product.get("productName") or "No encontrado"
                price = extraer_precio(product)
                link = normalizar_link(product.get("link"))

                resultados.append({
                    "descripcion": product_name.strip() if isinstance(product_name, str) else product_name,
                    "precio": formatear_precio_colones(price),
                    "url": link or "No encontrado",
                })

            if resultados:
                return {
                    "tienda": "MásxMenos",
                    "productos": resultados,
                    "mensaje": None,
                }

            return {
                "tienda": "MásxMenos",
                "productos": [],
                "mensaje": "No se encontraron productos para esta búsqueda.",
            }

        except requests.exceptions.JSONDecodeError:
            return {
                "tienda": "MásxMenos",
                "productos": [],
                "mensaje": "La respuesta no vino como JSON.",
            }

        except requests.exceptions.RequestException as e:
            if intento < reintentos:
                await asyncio.sleep(2)
            else:
                return {
                    "tienda": "MásxMenos",
                    "productos": [],
                    "mensaje": f"Error de conexión después de {reintentos} intentos: {str(e)}",
                }

        except Exception as e:
            if intento < reintentos:
                await asyncio.sleep(2)
            else:
                return {
                    "tienda": "MásxMenos",
                    "productos": [],
                    "mensaje": f"Error inesperado después de {reintentos} intentos: {str(e)}",
                }


# ---------------- Main para prueba ----------------
async def main():
    producto = input("🔎 Ingresa el producto a buscar en MásxMenos: ")
    max_resultados_input = input("🔹 Número máximo de resultados (por defecto 5): ")

    try:
        max_resultados = int(max_resultados_input)
    except ValueError:
        max_resultados = 5

    resultados = await buscar_masxmenos(producto, max_resultados)

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