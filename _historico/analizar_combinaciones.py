from collections import defaultdict
import re

from radar import buscar_noticias
from filtro import filtrar_noticias


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


def palabras_clave(titulo):

    texto = titulo.lower()

    texto = re.sub(
        r"[^\wáéíóúüñ-]",
        " ",
        texto
    )

    palabras = texto.split()

    return {
        palabra
        for palabra in palabras
        if len(palabra) >= 4
        and palabra not in PALABRAS_VACIAS
    }


noticias = buscar_noticias(
    "artificial intelligence",
    24
)

relevantes, _ = filtrar_noticias(
    noticias,
    "artificial intelligence"
)


combinaciones = defaultdict(list)


for noticia in relevantes:

    palabras = sorted(
        palabras_clave(
            noticia["title"]
        )
    )

    for i in range(len(palabras)):

        for j in range(i + 1, len(palabras)):

            combinacion = (
                palabras[i],
                palabras[j]
            )

            combinaciones[combinacion].append(
                noticia["title"]
            )


combinaciones_relevantes = [
    (combinacion, titulares)
    for combinacion, titulares
    in combinaciones.items()
    if len(titulares) >= 2
]


combinaciones_relevantes.sort(
    key=lambda x: len(x[1]),
    reverse=True
)


print()
print("=" * 80)
print("COMBINACIONES Y TITULARES")
print("=" * 80)


for (palabra_a, palabra_b), titulares in combinaciones_relevantes[:20]:

    print()
    print(
        f"{len(titulares)}  "
        f"{palabra_a} + {palabra_b}"
    )

    for titular in titulares:

        print(
            f"   - {titular}"
        )