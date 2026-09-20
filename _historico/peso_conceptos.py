from collections import Counter
import re

from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias


PALABRAS_RUIDO = {
    "revista",
    "magazine",
    "diari",
    "nación",
    "organización",
    "mundial",
    "canal26",
    "podría",
    "queda",
    "gana",
    "piden",
    "alerta",
    "contra",
    "como",
    "sobre",
}


def palabras_clave(noticia):

    titulo = noticia.get(
        "title",
        ""
    ).strip()

    fuente = noticia.get(
        "domain",
        ""
    ).strip()

    sufijo = f" - {fuente}"

    if titulo.endswith(sufijo):
        titulo = titulo[:-len(sufijo)].strip()

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
        and palabra not in PALABRAS_RUIDO
    }


noticias = buscar_noticias(
    "artificial intelligence",
    24
)

relevantes, _ = filtrar_noticias(
    noticias,
    "artificial intelligence"
)

grupos = agrupar_noticias(
    relevantes
)


frecuencia = Counter()


for grupo in grupos:

    noticia = grupo["noticias"][0]

    palabras = palabras_clave(
        noticia
    )

    frecuencia.update(
        palabras
    )


print()
print("=" * 80)
print("VALOR DE LOS CONCEPTOS")
print("=" * 80)


for palabra, cantidad in frecuencia.most_common(40):

    valor = 1 / cantidad

    print(
        f"{palabra:<20} "
        f"apariciones: {cantidad:>2} "
        f"valor: {valor:.3f}"
    )