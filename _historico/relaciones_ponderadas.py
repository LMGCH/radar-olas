from collections import Counter

from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias, palabras_clave


PALABRAS_RUIDO = {
    "para",
    "como",
    "sobre",
    "entre",
    "desde",
    "hasta",
    "también",
    "cuando",
    "donde",
    "porque",
    "según",
    "esta",
    "este",
    "estas",
    "estos",
    "esa",
    "ese",
    "esas",
    "esos",
    "muy",
    "más",
    "menos",
}


def conceptos(noticia):

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

    return palabras_clave(titulo)


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

conceptos_grupos = []


for grupo in grupos:

    noticia = grupo["noticias"][0]

    palabras = conceptos(
        noticia
    )

    conceptos_grupos.append(
        palabras
    )

    frecuencia.update(
        palabras
    )


def peso(palabra):

    return 1 / frecuencia[palabra]

def propagacion(grupo):

    publicaciones = grupo["publicaciones"]
    fuentes = grupo["fuentes"]

    return publicaciones + fuentes

relaciones = []


for i in range(len(grupos)):

    for j in range(i + 1, len(grupos)):

        comunes = (
            conceptos_grupos[i]
            & conceptos_grupos[j]
        )

        if len(comunes) < 2:
            continue

        fuerza = sum(
            peso(palabra)
            for palabra in comunes
        )

        propagacion_a = propagacion(
            grupos[i]
        )

        propagacion_b = propagacion(
            grupos[j]
        )

        propagacion_total = (
            propagacion_a
            + propagacion_b
        )

        relaciones.append(
            {
                "grupo_a": i,
                "grupo_b": j,
                "conceptos": sorted(comunes),
                "fuerza": fuerza,
                "propagacion": propagacion_total,
            }
        )


relaciones.sort(
    key=lambda x: x["fuerza"],
    reverse=True
)


print()
print("=" * 80)
print("RELACIONES PONDERADAS")
print("=" * 80)

print(
    f"Historias: {len(grupos)}"
)

print(
    f"Relaciones: {len(relaciones)}"
)

print()
print("TOP 30 RELACIONES")
print("=" * 80)


for numero, relacion in enumerate(
    relaciones[:30],
    start=1
):

    grupo_a = grupos[
        relacion["grupo_a"]
    ]

    grupo_b = grupos[
        relacion["grupo_b"]
    ]

    conceptos_comunes = ", ".join(
        relacion["conceptos"]
    )

    print(
        f"{numero:>2}. "
        f"Fuerza: {relacion['fuerza']:.3f} | "
        f"Propagación: {relacion['propagacion']}"
    )

    print(
        f"    Conceptos: "
        f"{conceptos_comunes}"
    )

    print(
        f"    A: {grupo_a['titulo']}"
    )

    print(
        f"    B: {grupo_b['titulo']}"
    )

    print(
        f"    A → publicaciones: "
        f"{grupo_a['publicaciones']} | "
        f"fuentes: {grupo_a['fuentes']}"
    )

    print(
        f"    B → publicaciones: "
        f"{grupo_b['publicaciones']} | "
        f"fuentes: {grupo_b['fuentes']}"
    )