from collections import Counter
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
    "una", "uno",
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

    return [
        palabra
        for palabra in palabras
        if len(palabra) >= 4
        and palabra not in PALABRAS_VACIAS
    ]


noticias = buscar_noticias(
    "artificial intelligence",
    24
)

relevantes, _ = filtrar_noticias(
    noticias,
    "artificial intelligence"
)


contador = Counter()

for noticia in relevantes:

    palabras = set(
        palabras_clave(
            noticia["title"]
        )
    )

    contador.update(palabras)


print()
print("=" * 80)
print("PALABRAS MÁS REPETIDAS")
print("=" * 80)

for palabra, cantidad in contador.most_common(40):

    print(
        f"{cantidad:>3}  {palabra}"
    )