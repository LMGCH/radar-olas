import re
import unicodedata

from sinonimos import SINONIMOS


# Variantes sencillas de conceptos que pueden aparecer
# expresados de forma diferente según el idioma.
VARIANTES_CONCEPTO = {
    "agentic ai": [
        "agentic ai",
        "ai agent",
        "ai agents",
        "agente de ia",
        "agentes de ia",
        "ia agentica",
        "ia agentico",
        "ia agéntica",
        "ia agéntico",
    ],
}


def normalizar(texto):
    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


def obtener_terminos(tema):
    """
    Devuelve los términos asociados al tema.
    """

    tema_normalizado = normalizar(tema)

    # Primero comprobamos variantes específicas.
    for clave, variantes in VARIANTES_CONCEPTO.items():

        clave_normalizada = normalizar(clave)

        if tema_normalizado == clave_normalizada:

            return [
                normalizar(termino)
                for termino in variantes
            ]

        for variante in variantes:

            if tema_normalizado == normalizar(variante):

                return [
                    normalizar(termino)
                    for termino in variantes
                ]

    # Después utilizamos el diccionario general.
    for clave, terminos in SINONIMOS.items():

        clave_normalizada = normalizar(clave)

        if tema_normalizado == clave_normalizada:

            return [
                normalizar(termino)
                for termino in terminos
            ]

        for termino in terminos:

            if tema_normalizado == normalizar(termino):

                return [
                    normalizar(t)
                    for t in terminos
                ]

    # Si no conocemos el concepto,
    # utilizamos el término introducido por el usuario.
    return [tema_normalizado]


def contiene_termino(texto, termino):
    """
    Comprueba si un término aparece como palabra
    o expresión independiente.
    """

    texto = normalizar(texto)
    termino = normalizar(termino)

    if not texto or not termino:
        return False

    palabras_texto = set(texto.split())
    palabras_termino = termino.split()

    # Expresión formada por varias palabras.
    if len(palabras_termino) > 1:
        return termino in texto

    # Palabra individual.
    return termino in palabras_texto


def es_relevante(noticia, tema):
    """
    Determina si una noticia es relevante para el tema.
    """

    titulo = noticia.get("title", "")

    terminos = obtener_terminos(tema)

    for termino in terminos:

        if contiene_termino(titulo, termino):
            return True

    return False


def filtrar_noticias(noticias, tema):
    """
    Separa las noticias relevantes de las descartadas.
    """

    relevantes = []
    descartadas = []

    for noticia in noticias:

        if es_relevante(noticia, tema):

            relevantes.append(noticia)

        else:

            descartadas.append(noticia)

    return relevantes, descartadas