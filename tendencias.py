import requests
import xml.etree.ElementTree as ET


FUENTES_TENDENCIAS = {
    "🌍 Global": [
        "US",
        "GB",
        "DE",
        "FR",
        "JP",
        "KR",
        "IN",
    ],
    "🇪🇺 Europa": [
        "GB",
        "DE",
        "FR",
        "ES",
    ],
    "🇺🇸 EE. UU.": [
        "US",
    ],
    "🇪🇸 España": [
        "ES",
    ],
}


def obtener_tendencias_pais(geo, maximo=10):
    """
    Obtiene las tendencias actuales de Google Trends
    para un país o región concreta.

    Devuelve únicamente los títulos.
    """

    url = (
        "https://trends.google.com/trending/rss"
        f"?geo={geo}"
    )

    try:
        respuesta = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Radar-de-Olas/0.1"
            }
        )

        respuesta.raise_for_status()

        raiz = ET.fromstring(
            respuesta.content
        )

        tendencias = []

        for item in raiz.findall(".//item"):

            titulo = item.findtext("title")

            if titulo:
                tendencias.append(
                    titulo.strip()
                )

            if len(tendencias) >= maximo:
                break

        return tendencias

    except Exception as e:

        print(
            f"ERROR TENDENCIAS GOOGLE TRENDS "
            f"{geo}: {e}"
        )

        return []


def obtener_tendencias_mundiales(maximo=10):
    """
    Obtiene tendencias de varios mercados
    para construir una visión internacional.

    Reparte los resultados entre los mercados
    y elimina duplicados.

    No interviene en el motor de Radar de Olas.
    """

    tendencias_por_pais = {}

    for geo in FUENTES_TENDENCIAS["🌍 Global"]:

        tendencias_por_pais[geo] = obtener_tendencias_pais(
            geo,
            maximo=maximo
        )

    resultados = []

    posicion = 0

    while len(resultados) < maximo:

        añadidas_en_vuelta = 0

        for geo in FUENTES_TENDENCIAS["🌍 Global"]:

            tendencias = tendencias_por_pais.get(
                geo,
                []
            )

            if posicion >= len(tendencias):
                continue

            tendencia = tendencias[posicion]

            if tendencia not in resultados:

                resultados.append(tendencia)
                añadidas_en_vuelta += 1

            if len(resultados) >= maximo:
                break

        if añadidas_en_vuelta == 0:
            break

        posicion += 1

    return resultados