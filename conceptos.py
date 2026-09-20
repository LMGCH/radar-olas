from collections import Counter

from agrupador import palabras_clave

def traducir_concepto(concepto):
    """
    Traduce un concepto del inglés al español usando Argos Translate.
    Si no puede traducirlo, conserva el original.
    """
    try:
        import argostranslate.translate as translate
        return translate.translate(concepto, "en", "es")
    except Exception:
        return concepto


PALABRAS_RUIDO_CONCEPTOS = {
    "news",
    "yahoo",
    "into",
    "what",
    "this",
    "that",
    "with",
    "from",
    "about",
    "after",
    "before",
    "over",
    "under",
    "more",
    "than",
    "their",
    "they",
    "them",
    "have",
    "has",
    "been",
    "will",
    "could",
    "would",
    "should",
    "said",
    "says",
    "according",
    "report",
    "reports",
    "today",
    "latest",
    "breaking",

    # Lenguaje periodístico frecuente
    "post",
    "posts",
    "calls",
    "call",
    "amid",
    "world",
    "name",
    "names",
}


def detectar_conceptos_relacionados(
    historias,
    tema=None,
    tema_internacional=None,
    minimo_historias=2,
    max_resultados=10,
):
    """
    Detecta términos que aparecen en varias historias.

    Esta función solo ayuda a descubrir posibles búsquedas
    relacionadas. No modifica las historias ni interviene
    en la detección de señales.
    """

    palabras_tema = set()

    if tema:
        palabras_tema = set(
            palabras_clave(tema)
        )

    if tema_internacional:
        palabras_tema.update(
            palabras_clave(tema_internacional)
        )

    apariciones = Counter()

    for historia in historias:

        conceptos_historia = set()

        for noticia in historia.get(
            "noticias",
            []
        ):

            titulo = noticia.get(
                "title",
                ""
            )

            conceptos = palabras_clave(titulo)

            if tema_internacional:
                conceptos = {
                    traducir_concepto(concepto)
                    for concepto in conceptos
                }

            conceptos_historia.update(conceptos)

        conceptos_historia -= palabras_tema
        conceptos_historia -= PALABRAS_RUIDO_CONCEPTOS

        for concepto in conceptos_historia:
            apariciones[concepto] += 1

    resultados = [
        {
            "concepto": concepto,
            "historias": cantidad,
        }
        for concepto, cantidad in apariciones.items()
        if cantidad >= minimo_historias
    ]

    resultados.sort(
        key=lambda resultado: (
            resultado["historias"],
            resultado["concepto"],
        ),
        reverse=True
    )

    return resultados[:max_resultados]
