import os
import re
import time
from datetime import datetime
import xml.etree.ElementTree as ET

import requests
import pandas as pd
from bs4 import BeautifulSoup

# Probamos más de un feed por si uno cambia o devuelve vacío
FEED_URLS = [
    "https://es.mongabay.com/feed/",                 # feed general (muy común en WP)
    "https://es.mongabay.com/feed/?post_type=post",  # alternativo
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

MAX_ARTICULOS = 50
OUTPUT_CSV = "data/mongabay_50_articulos_raw.csv"


def limpiar_texto(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_rss_items(xml_text: str) -> list[dict]:
    """
    Parsea RSS (XML) sin BeautifulSoup (evita lxml).
    Devuelve: titulo, url, fecha_publicacion, autor_feed
    """
    root = ET.fromstring(xml_text)

    # Namespaces típicos en RSS (dc:creator)
    ns = {"dc": "http://purl.org/dc/elements/1.1/"}

    items = []
    for item in root.findall(".//item"):
        titulo = limpiar_texto(item.findtext("title", default=""))
        url = limpiar_texto(item.findtext("link", default=""))
        pub_date_raw = limpiar_texto(item.findtext("pubDate", default=""))

        # autor en dc:creator
        creator = item.find("dc:creator", ns)
        autor = limpiar_texto(creator.text) if creator is not None and creator.text else ""

        # Normalizar fecha a YYYY-MM-DD si tiene formato RSS estándar
        fecha_iso = ""
        if pub_date_raw:
            try:
                dt = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                fecha_iso = dt.date().isoformat()
            except ValueError:
                fecha_iso = pub_date_raw  # fallback

        if url:
            items.append(
                {
                    "titulo": titulo,
                    "fecha_publicacion": fecha_iso,
                    "url": url,
                    "autor_feed": autor,
                }
            )

    return items


def get_feed_items() -> list[dict]:
    """
    Intenta varios feeds hasta encontrar items.
    """
    for feed_url in FEED_URLS:
        try:
            xml_text = fetch(feed_url)
            items = parse_rss_items(xml_text)
            if items:
                print(f"[OK] RSS leído: {feed_url} | items: {len(items)}")
                return items
            else:
                print(f"[WARN] RSS sin items: {feed_url}")
        except Exception as e:
            print(f"[WARN] No se pudo leer feed {feed_url} | {e}")

    return []


def get_soup_html(url: str) -> BeautifulSoup:
    html = fetch(url)
    return BeautifulSoup(html, "html.parser")


def extraer_texto_articulo(soup: BeautifulSoup) -> str:
    candidates = [
        "div.entry-content",
        "article .entry-content",
        "div.td-post-content",
        "div.post-content",
        "div.single-content",
        "article",
    ]

    container = None
    for sel in candidates:
        container = soup.select_one(sel)
        if container:
            break

    if not container:
        return ""

    parts = []
    for el in container.find_all(["p", "h2", "h3", "li"], recursive=True):
        txt = limpiar_texto(el.get_text(" ", strip=True))
        if txt:
            parts.append(txt)

    return limpiar_texto(" ".join(parts))


def extraer_autor_y_fecha_de_pagina(soup: BeautifulSoup) -> tuple[str, str]:
    autor = ""
    fecha = ""

    # Autor
    autor_sel = [
        "a[rel='author']",
        ".author a",
        ".byline a",
        ".byline",
        ".author-name",
        "span.author",
    ]
    for sel in autor_sel:
        el = soup.select_one(sel)
        if el:
            autor = limpiar_texto(el.get_text())
            if autor:
                break

    # Fecha
    time_el = soup.select_one("time[datetime]")
    if time_el and time_el.get("datetime"):
        fecha = limpiar_texto(time_el.get("datetime"))
        if "T" in fecha:
            fecha = fecha.split("T")[0]

    return autor, fecha


def main():
    # 1) Leer RSS
    feed_items = get_feed_items()
    if not feed_items:
        raise RuntimeError("No se pudieron leer items del RSS. Revisa conectividad o cambia FEED_URLS.")

    os.makedirs("data", exist_ok=True)

    articulos = []
    vistos = set()

    # 2) Tomar 50 artículos válidos (while visible + ifs)
    i = 0
    while len(articulos) < MAX_ARTICULOS and i < len(feed_items):
        item = feed_items[i]
        i += 1

        url = item["url"]
        if not url or url in vistos:
            continue
        vistos.add(url)

        try:
            soup = get_soup_html(url)
        except Exception as e:
            print(f"[WARN] No se pudo abrir: {url} | {e}")
            continue

        texto = extraer_texto_articulo(soup)
        autor_pagina, fecha_pagina = extraer_autor_y_fecha_de_pagina(soup)

        autor_final = autor_pagina if autor_pagina else item.get("autor_feed", "")
        fecha_final = fecha_pagina if fecha_pagina else item.get("fecha_publicacion", "")

        # filtro mínimo: evita páginas raras/bloqueadas
        if len(texto) < 200:
            print(f"[SKIP] Texto muy corto: {url}")
            continue

        articulos.append(
            {
                "titulo": item.get("titulo", ""),
                "fecha_publicacion": fecha_final,
                "url": url,
                "autor": autor_final,
                "texto": texto,
            }
        )

        print(f"[OK] {len(articulos)}/{MAX_ARTICULOS} -> {item.get('titulo','(sin título)')}")
        time.sleep(1)

    # 3) Guardar CSV
    df = pd.DataFrame(articulos).drop_duplicates(subset=["url"])
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\n✅ OK: {len(df)} artículos guardados en {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
