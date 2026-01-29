# -*- coding: utf-8 -*-
"""
02_process_mongabay.py
Limpieza + procesamiento desde el CSV raw de extracción.

Salida:
- data/mongabay_procesado.csv  (1 fila = 1 artículo)
- data/mongabay_tops.csv       (top 5 temas, top 5 países)
- data/mongabay_top20_palabras.csv (top 20 palabras globales)

Requisitos:
pip install pandas
(BeautifulSoup/requests no son necesarios aquí)
"""

import os
import re
import unicodedata
from collections import Counter
from datetime import datetime

import pandas as pd

INPUT_RAW = "data/mongabay_50_articulos_raw.csv"
OUTPUT_MAIN = "data/mongabay_procesado.csv"
OUTPUT_TOPS = "data/mongabay_tops.csv"
OUTPUT_TOP20 = "data/mongabay_top20_palabras.csv"


# Stopwords básicas en español (suficientes para el curso)
STOPWORDS_ES = {
    "a", "al", "algo", "algunos", "ante", "antes", "aqui", "así", "asi", "aún", "aun",
    "bajo", "bien", "cada", "casi", "como", "con", "contra", "cual", "cuales", "cuando",
    "de", "del", "desde", "donde", "dos", "el", "ella", "ellas", "ellos", "en", "entre",
    "era", "es", "esa", "esas", "ese", "eso", "esos", "esta", "está", "esta", "estaban",
    "estas", "este", "esto", "estos", "estoy", "fin", "fue", "fueron", "ha", "han",
    "hasta", "hay", "la", "las", "le", "les", "lo", "los", "más", "mas", "me", "mi",
    "mis", "mismo", "muy", "no", "nos", "nuestra", "nuestro", "o", "otra", "otras",
    "otro", "otros", "para", "pero", "poco", "por", "porque", "que", "qué", "se", "sea",
    "según", "segun", "ser", "si", "sí", "sin", "sobre", "son", "su", "sus", "también",
    "tambien", "te", "tener", "tiene", "tienen", "toda", "todas", "todo", "todos", "tu",
    "tus", "un", "una", "uno", "unos", "y", "ya", "yo", "u", "e", "ni", "muy",
    # comunes en noticias
    "años", "año", "hoy", "ayer", "día", "dias", "día", "días"
}


# Lista corta (pero útil) de países para inferir "pais"
PAISES_LATAM = [
    "argentina", "bolivia", "brasil", "chile", "colombia", "costa rica", "cuba",
    "ecuador", "el salvador", "guatemala", "honduras", "mexico", "méxico",
    "nicaragua", "panama", "panamá", "paraguay", "peru", "perú", "republica dominicana",
    "república dominicana", "uruguay", "venezuela",
    # territorios/regiones frecuentes
    "amazonía", "amazonia", "patagonia", "andes"
]


# Diccionario simple de temas por palabras clave (ajústalo si tu corpus lo necesita)
TEMA_KEYWORDS = {
    "Deforestación y bosques": [
        "deforest", "tala", "bosque", "incend", "madera", "reforest", "orest"
    ],
    "Minería y extractivismo": [
        "minería", "mineria", "oro", "cobre", "litio", "petróleo", "petroleo", "gas",
        "hidrocarb", "extractiv", "pozo", "concesión", "concesion"
    ],
    "Biodiversidad y fauna": [
        "biodivers", "especie", "fauna", "flora", "jaguar", "delfín", "delfin",
        "mono", "ave", "anfib", "reptil", "mamífer", "mamifer", "extinción", "extincion"
    ],
    "Pueblos indígenas y territorio": [
        "indígen", "indigen", "comunidad", "territorio", "consulta previa", "ancestral",
        "pueblos", "lider", "líder", "defensor", "defensora"
    ],
    "Agua y contaminación": [
        "agua", "río", "rio", "laguna", "humedal", "contamin", "mercurio",
        "derrames", "derrame", "residuos", "plástico", "plastico"
    ],
    "Clima y energía": [
        "clima", "cambio climático", "cambio climatico", "emision", "emisiones", "carbono",
        "sequía", "sequia", "inund", "temperatura", "energía", "energia", "renovable"
    ],
}


def asegurar_directorio(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def normalizar_espacios(s: str) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s


def quitar_tildes(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def normalizar_texto_basico(s: str) -> str:
    """Minúsculas + limpiar espacios/saltos."""
    s = "" if s is None else str(s)
    s = s.lower()
    s = normalizar_espacios(s)
    return s


def parsear_fecha_a_ddmmyyyy(s: str) -> str:
    """
    Intenta convertir distintos formatos a dd/mm/YYYY.
    Si no se puede, devuelve "".
    """
    if not s:
        return ""

    s = str(s).strip()

    # Si viene ISO: 2025-01-28 o 2025-01-28T...
    try:
        if "T" in s:
            s2 = s.split("T")[0]
        else:
            s2 = s
        dt = datetime.strptime(s2, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        pass

    # Formato dd/mm/yyyy ya
    try:
        dt = datetime.strptime(s, "%d/%m/%Y")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        pass

    # Formato dd-mm-yyyy
    try:
        dt = datetime.strptime(s, "%d-%m-%Y")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        pass

    return ""


def inferir_pais(texto: str) -> str:
    """
    Heurística: busca países en el texto (sin tildes).
    Devuelve el primer match encontrado o 'Regional/LatAm'.
    """
    t = quitar_tildes(texto.lower())
    for pais in PAISES_LATAM:
        p = quitar_tildes(pais.lower())
        # match por palabra/frase
        if re.search(rf"\b{re.escape(p)}\b", t):
            # normaliza a forma "bonita"
            if p in ("mexico",):
                return "México"
            if p in ("peru",):
                return "Perú"
            if p in ("panama",):
                return "Panamá"
            if p in ("republica dominicana",):
                return "República Dominicana"
            if p == "amazonia" or p == "amazonía":
                return "Amazonía"
            if p == "andes":
                return "Andes"
            if p == "patagonia":
                return "Patagonia"
            return pais.title()
    return "Regional/LatAm"


def inferir_tema(texto: str) -> str:
    """
    Clasificación simple por keywords.
    Devuelve la categoría con más coincidencias.
    Si no hay coincidencias, 'Otros/No clasificado'.
    """
    t = quitar_tildes(texto.lower())
    scores = {}
    for tema, kws in TEMA_KEYWORDS.items():
        score = 0
        for kw in kws:
            k = quitar_tildes(kw.lower())
            if k and k in t:
                # cuenta ocurrencias aproximadas
                score += t.count(k)
        scores[tema] = score

    tema_ganador = max(scores, key=scores.get)
    if scores[tema_ganador] == 0:
        return "Otros/No clasificado"
    return tema_ganador


def tokenizar(texto: str) -> list[str]:
    """
    Tokeniza a palabras (solo letras), quita stopwords y tokens muy cortos.
    """
    t = quitar_tildes(texto.lower())
    # solo letras y espacios
    t = re.sub(r"[^a-zñ\s]", " ", t)
    t = normalizar_espacios(t)

    tokens = []
    for w in t.split(" "):
        if not w:
            continue
        if len(w) < 3:
            continue
        if w in STOPWORDS_ES:
            continue
        tokens.append(w)
    return tokens


def top_n_palabras(texto: str, n: int = 5) -> str:
    """
    Devuelve string con las top N palabras (separadas por coma) del artículo.
    """
    tokens = tokenizar(texto)
    if not tokens:
        return ""
    c = Counter(tokens)
    top = [w for w, _ in c.most_common(n)]
    return ", ".join(top)


def main():
    asegurar_directorio(OUTPUT_MAIN)

    df = pd.read_csv(INPUT_RAW, encoding="utf-8")

    # --- LIMPIEZA ---
    # 1) Quitar duplicados por URL
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"])
    else:
        df = df.drop_duplicates()

    # 2) Manejo de vacíos
    # Autor
    if "autor" not in df.columns:
        df["autor"] = ""
    df["autor"] = df["autor"].fillna("").astype(str)
    df["autor_faltante"] = df["autor"].str.strip().eq("")
    df.loc[df["autor_faltante"], "autor"] = "Desconocido"

    # Fecha
    if "fecha_publicacion" not in df.columns:
        df["fecha_publicacion"] = ""
    df["fecha_publicacion"] = df["fecha_publicacion"].fillna("").astype(str)

    # 3) Normalización texto base: minúsculas + espacios
    for col in ["titulo", "texto"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).apply(normalizar_texto_basico)

    # 4) Convertir fecha a dd/mm/YYYY
    df["fecha_publicacion_norm"] = df["fecha_publicacion"].apply(parsear_fecha_a_ddmmyyyy)
    df["fecha_faltante"] = df["fecha_publicacion_norm"].str.strip().eq("")
    df.loc[df["fecha_faltante"], "fecha_publicacion_norm"] = "Sin fecha"

    # --- PROCESAMIENTO ---
    # longitud_palabras (sobre el texto normalizado)
    df["longitud_palabras"] = df["texto"].apply(lambda x: len(tokenizar(x)))

    # tema y país usando texto + titulo (mejor cobertura)
    df["texto_total"] = (df["titulo"].fillna("") + " " + df["texto"].fillna("")).astype(str)

    df["tema"] = df["texto_total"].apply(inferir_tema)
    df["pais"] = df["texto_total"].apply(inferir_pais)

    # 5 palabras más repetidas por artículo
    df["top5_palabras_articulo"] = df["texto"].apply(lambda x: top_n_palabras(x, n=5))

    # --- CSV PRINCIPAL (un solo CSV) ---
    df_out = df[[
        "titulo",
        "fecha_publicacion_norm",
        "url",
        "autor",
        "tema",
        "pais",
        "top5_palabras_articulo",
        "longitud_palabras",
    ]].rename(columns={"fecha_publicacion_norm": "fecha_publicacion"})

    df_out.to_csv(OUTPUT_MAIN, index=False, encoding="utf-8")
    print(f"✅ Guardado: {OUTPUT_MAIN} | filas: {len(df_out)}")

    # --- CSV TOPS (top 5 temas y top 5 países) ---
    top_temas = df_out["tema"].value_counts().head(5).reset_index()
    top_temas.columns = ["valor", "conteo"]
    top_temas.insert(0, "tipo", "Top 5 temas")

    top_paises = df_out["pais"].value_counts().head(5).reset_index()
    top_paises.columns = ["valor", "conteo"]
    top_paises.insert(0, "tipo", "Top 5 países")

    df_tops = pd.concat([top_temas, top_paises], ignore_index=True)
    df_tops.to_csv(OUTPUT_TOPS, index=False, encoding="utf-8")
    print(f"✅ Guardado: {OUTPUT_TOPS}")

    # --- CSV TOP 20 PALABRAS GLOBALES ---
    all_tokens = []
    for t in df["texto"].tolist():
        all_tokens.extend(tokenizar(t))

    top20 = Counter(all_tokens).most_common(20)
    df_top20 = pd.DataFrame(top20, columns=["palabra", "conteo"])
    df_top20.to_csv(OUTPUT_TOP20, index=False, encoding="utf-8")
    print(f"✅ Guardado: {OUTPUT_TOP20}")


if __name__ == "__main__":
    main()
