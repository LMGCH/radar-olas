import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from email.utils import parsedate_to_datetime

from sinonimos import SINONIMOS


def _obtener_consulta_internacional(tema):
    """
    Obtiene el término en inglés cuando existe en sinonimos.py.
    Si no existe, utiliza el tema original.
    """

    tema_normalizado = tema.strip().lower()

    for clave, terminos in SINONIMOS.items():

        if clave.lower() == tema_normalizado:

            for termino in terminos:
                if termino.lower() != tema_normalizado:
                    return termino

    return tema

def _traducir_consulta_internacional(tema):
    """
    Traduce una consulta del español al inglés usando Argos Translate.
    Si la traducción falla, devuelve el tema original.
    """

    try:

        import argostranslate.translate as translate

        return translate.translate(
            tema,
            "es",
            "en",
        )

    except Exception:

        return tema

def _normalizar_consulta_internacional(tema):
    """
    Convierte una consulta en inglés en una búsqueda internacional
    breve y centrada en los conceptos más relevantes.

    La consulta final tendrá como máximo 4 palabras.
    """

    palabras_vacias = {
        "the", "a", "an",
        "in", "on", "at", "of",
        "for", "to", "from",
        "and", "or", "but",
        "between", "with",
        "about", "into",
        "by", "as",
        "latest", "news",
        "hits", "advances",
        "discovery",
    }

    palabras = tema.lower().split()

    palabras_significativas = [
        palabra
        for palabra in palabras
        if palabra not in palabras_vacias
    ]

    return " ".join(palabras_significativas[:5])

def _buscar_google_news(tema, horas, idioma, pais, ceid):
    """
    Realiza una búsqueda en Google News RSS con una configuración
    concreta de idioma y país.
    """

    if horas < 24:
        periodo = f"{horas}h"
    elif horas < 168:
        periodo = f"{horas}h"
    else:
        periodo = "7d"

    consulta = quote(f"{tema} when:{periodo}")

    url = (
        "https://news.google.com/rss/search"
        f"?q={consulta}"
        f"&hl={idioma}"
        f"&gl={pais}"
        f"&ceid={ceid}"
    )

    respuesta = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Radar-de-Olas/0.1"
        },
    )

    respuesta.raise_for_status()

    raiz = ET.fromstring(respuesta.content)

    noticias = []

    for item in raiz.findall("./channel/item"):

        titulo = item.findtext("title", "")
        enlace = item.findtext("link", "")
        fecha = item.findtext("pubDate", "")
        fuente = item.findtext("source", "")

        try:
            fecha_dt = parsedate_to_datetime(fecha)
        except (TypeError, ValueError):
            fecha_dt = None

        noticias.append(
            {
                "title": titulo,
                "url": enlace,
                "seendate": fecha,
                "datetime": fecha_dt,
                "domain": fuente,
            }
        )

    noticias.sort(
        key=lambda x: x["datetime"] or parsedate_to_datetime(
            "Thu, 01 Jan 1970 00:00:00 GMT"
        ),
        reverse=True,
    )

    return noticias


def buscar_noticias(tema, horas=24):
    """
    Busca noticias en España.
    Consulta en español y utiliza el contexto de Google News España.
    """

    return _buscar_google_news(
        tema,
        horas,
        idioma="es",
        pais="ES",
        ceid="ES:es",
    )


def buscar_noticias_internacionales(tema, horas=24):
    """
    Busca noticias internacionales.

    Traduce y normaliza la consulta del usuario al inglés
    y devuelve tanto las noticias como la consulta internacional
    utilizada para realizar la búsqueda.
    """

    tema_internacional = _obtener_consulta_internacional(tema)

    if tema_internacional == tema:
        tema_internacional = _traducir_consulta_internacional(
            tema
        )

    tema_internacional = _normalizar_consulta_internacional(
        tema_internacional
    )

    noticias = _buscar_google_news(
        tema_internacional,
        horas,
        idioma="en",
        pais="US",
        ceid="US:en",
    )

    return noticias, tema_internacional


def buscar_noticias_gdelt(tema, horas=24):
    ...