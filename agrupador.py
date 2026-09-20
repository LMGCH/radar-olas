import re

from filtro import normalizar, obtener_terminos


PALABRAS_VACIAS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "y", "o", "en", "con", "por", "para",
    "que", "se", "su", "sus", "es", "como", "más", "ya",
    "sobre", "entre", "desde", "tras", "ante", "sin",
    "esta", "este", "estas", "estos",
    "también", "pero", "mientras",
    "this", "the", "a", "an", "of", "and", "in", "on",
    "for", "to", "with", "from", "new", "how", "why"
}

def palabras_clave(titulo, palabras_tema=None):
    texto = normalizar(titulo)

    palabras = texto.split()

    if palabras_tema:
        palabras = [
            palabra
            for palabra in palabras
            if palabra not in palabras_tema
        ]

    return {
        palabra
        for palabra in palabras
        if len(palabra) >= 4
        and palabra not in PALABRAS_VACIAS
    }

def similitud(titulo_a, titulo_b, palabras_tema=None):
    palabras_a = palabras_clave(
        titulo_a,
        palabras_tema
    )

    palabras_b = palabras_clave(
        titulo_b,
        palabras_tema
    )

    if not palabras_a or not palabras_b:
        return 0

    comunes = palabras_a & palabras_b

    if len(comunes) < 2:
        return 0

    return len(comunes) / min(
        len(palabras_a),
        len(palabras_b)
    )

def fuente(noticia):
    return noticia.get(
        "domain",
        "Desconocida"
    )


def agrupar_noticias(
    noticias,
    umbral=0.40,
    tema=None
):

    palabras_tema = set()

    if tema:
        for termino in obtener_terminos(tema):
            palabras_tema.update(
                normalizar(termino).split()
            )

    grupos = []

    for noticia in noticias:

        titulo = noticia.get(
            "title",
            ""
        )

        grupo_encontrado = None

        for grupo in grupos:

            similitudes = [
                similitud(
                    titulo,
                    otra.get("title", ""),
                    palabras_tema
                )
                for otra in grupo["noticias"]
            ]

            if max(
                similitudes,
                default=0
            ) >= umbral:

                grupo_encontrado = grupo
                break

        if grupo_encontrado:

            grupo_encontrado["noticias"].append(
                noticia
            )

        else:

            grupos.append(
                {
                    "titulo": titulo,
                    "noticias": [noticia],
                }
            )

    for grupo in grupos:

        publicaciones = grupo["noticias"]

        grupo["publicaciones"] = len(
            publicaciones
        )

        grupo["fuentes"] = len(
            {
                fuente(noticia)
                for noticia in publicaciones
            }
        )

        grupo["lista_fuentes"] = sorted(
            {
                fuente(noticia)
                for noticia in publicaciones
            }
        )

    grupos.sort(
        key=lambda grupo: (
            grupo["fuentes"],
            grupo["publicaciones"]
        ),
        reverse=True
    )

    return grupos