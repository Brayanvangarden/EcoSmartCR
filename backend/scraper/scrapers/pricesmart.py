import asyncio
import time
import random
import urllib.parse

import requests

BASE_URL = "https://www.pricesmart.com"
API_URL = "https://www.pricesmart.com/api/br_discovery/getProductsByKeyword"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

ACCOUNT_ID = "7024"
AUTH_KEY = "ev7libhybjg5h1d1"
DOMAIN_KEY = "pricesmart_bloomreach_io_en"
VIEW_ID = "CR"

FIELDS = (
    "pid,title,price,thumb_image,brand,slug,skuid,currency,fractionDigits,"
    "master_sku,sold_by_weight_CR,weight_CR,weight_uom_description_CR,"
    "sign_price_CR,price_per_uom_CR,uom_description_CR,saving_amount_CR,"
    "original_price_without_saving_CR,availability_CR,price_CR,inventory_CR,"
    "inventory_CR,promoid_CR"
)


def generar_br_uid() -> str:
    timestamp_ms = int(time.time() * 1000)
    random_uid = random.randint(10**12, 10**13 - 1)

    return f"uid={random_uid}:v=15.0:ts={timestamp_ms}:hc=1"


def generar_request_id() -> int:
    return int(time.time() * 1000)


def construir_payload_pricesmart(producto: str, max_resultados: int) -> dict:
    producto = producto.strip()
    encoded_query = urllib.parse.quote(producto, safe="")

    search_url = f"{BASE_URL}/en-cr/search?q={encoded_query}"

    return {
        "url": search_url,
        "start": 0,
        "q": producto,
        "fq": [],
        "search_type": "keyword",
        "rows": max_resultados,
        "ref_url": search_url,
        "account_id": ACCOUNT_ID,
        "auth_key": AUTH_KEY,
        "_br_uid_2": generar_br_uid(),
        "request_id": generar_request_id(),
        "domain_key": DOMAIN_KEY,
        "fl": FIELDS,
        "view_id": VIEW_ID,
    }


def obtener_json_sync(producto: str, max_resultados: int, timeout: int = 60) -> dict:
    payload = construir_payload_pricesmart(producto, max_resultados)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/en-cr/search?q={urllib.parse.quote(producto, safe='')}",
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def obtener_productos(payload: dict) -> list:
    """
    Bloomreach normalmente devuelve productos en:
    response.docs
    """
    response_data = payload.get("response", {})

    if isinstance(response_data, dict):
        docs = response_data.get("docs", [])

        if isinstance(docs, list):
            return docs

    return []


def formatear_precio_colones(price):
    if price is None or price == "No encontrado":
        return "No encontrado"

    try:
        return f"¢{float(price):,.2f}"
    except (ValueError, TypeError):
        return "No encontrado"


def construir_url_producto(product: dict) -> str:
    slug = product.get("slug")
    pid = product.get("pid")

    if slug:
        if slug.startswith("http"):
            return slug

        if slug.startswith("/"):
            return f"{BASE_URL}{slug}"

        return f"{BASE_URL}/en-cr/product/{slug}"

    if pid:
        return f"{BASE_URL}/en-cr/product/{pid}"

    return "No encontrado"


def extraer_precio(product: dict):
    """
    PriceSmart puede devolver precio en varias propiedades.
    Se prioriza price_CR si existe; si no, price.
    """
    price = product.get("price_CR")

    if price is not None:
        return price

    price = product.get("price")

    if price is not None:
        return price

    sign_price = product.get("sign_price_CR")

    if sign_price is not None:
        return sign_price

    return None


async def buscar_pricesmart(query: str, max_resultados: int = 5, reintentos: int = 3):
    for intento in range(1, reintentos + 1):
        try:
            payload = await asyncio.to_thread(
                obtener_json_sync,
                query,
                max_resultados,
            )

            products = obtener_productos(payload)

            resultados = []

            for product in products[:max_resultados]:
                title = product.get("title") or "No encontrado"
                price = extraer_precio(product)
                product_url = construir_url_producto(product)

                resultados.append({
                    "descripcion": title.strip() if isinstance(title, str) else title,
                    "precio": formatear_precio_colones(price),
                    "url": product_url,
                })

            if resultados:
                return {
                    "tienda": "PriceSmart",
                    "productos": resultados,
                    "mensaje": None,
                }

            return {
                "tienda": "PriceSmart",
                "productos": [],
                "mensaje": "No se encontraron productos para esta búsqueda.",
            }

        except requests.exceptions.JSONDecodeError:
            return {
                "tienda": "PriceSmart",
                "productos": [],
                "mensaje": "La respuesta no vino como JSON.",
            }

        except requests.exceptions.RequestException as e:
            if intento < reintentos:
                await asyncio.sleep(2)
            else:
                return {
                    "tienda": "PriceSmart",
                    "productos": [],
                    "mensaje": f"Error de conexión después de {reintentos} intentos: {str(e)}",
                }

        except Exception as e:
            if intento < reintentos:
                await asyncio.sleep(2)
            else:
                return {
                    "tienda": "PriceSmart",
                    "productos": [],
                    "mensaje": f"Error inesperado después de {reintentos} intentos: {str(e)}",
                }


# ---------------- Main para prueba ----------------
async def main():
    producto = input("🔎 Ingresa el producto a buscar en PriceSmart: ")
    max_resultados_input = input("🔹 Número máximo de resultados (por defecto 5): ")

    try:
        max_resultados = int(max_resultados_input)
    except ValueError:
        max_resultados = 5

    resultados = await buscar_pricesmart(producto, max_resultados)

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