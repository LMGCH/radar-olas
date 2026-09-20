from radar import (
    buscar_noticias,
    buscar_noticias_internacionales,
)
from filtro import filtrar_noticias
from agrupador import agrupar_noticias
from senales import (
    detectar_relaciones,
    comparar_internacional_espana,
    calcular_brecha_internacional_espana,
)


tema = "artificial intelligence"


print("1. Buscando noticias internacionales...")

noticias_internacionales, consulta_internacional = (
    buscar_noticias_internacionales(
        tema,
        24
    )
)


print(
    "Noticias internacionales recibidas:",
    len(noticias_internacionales)
)


print(
    "Consulta internacional:",
    consulta_internacional
)


print()
print("2. Filtrando internacionales...")

relevantes_internacionales, _ = filtrar_noticias(
    noticias_internacionales,
    tema
)


print(
    "Noticias internacionales relevantes:",
    len(relevantes_internacionales)
)


print()
print("3. Agrupando internacionales...")

historias_internacionales = agrupar_noticias(
    relevantes_internacionales,
    tema=tema
)


print(
    "Historias internacionales:",
    len(historias_internacionales)
)


print()
print("4. Buscando noticias en España...")

noticias_espana = buscar_noticias(
    tema,
    24
)


print(
    "Noticias España recibidas:",
    len(noticias_espana)
)


print()
print("5. Filtrando España...")

relevantes_espana, _ = filtrar_noticias(
    noticias_espana,
    tema
)


print(
    "Noticias España relevantes:",
    len(relevantes_espana)
)


print()
print("6. Agrupando España...")

historias_espana = agrupar_noticias(
    relevantes_espana,
    tema=tema
)


print(
    "Historias España:",
    len(historias_espana)
)

print()
print("7. Buscando relaciones internacionales...")

relaciones = detectar_relaciones(
    historias_internacionales
)


print(
    "Relaciones detectadas:",
    len(relaciones)
)


print(
    "Relaciones detectadas:",
    len(relaciones)
)


print()
print("=" * 80)
print("RELACIONES ENTRE HISTORIAS")
print("=" * 80)


for relacion in relaciones:

    grupo_a = historias_internacionales[
        relacion["grupo_a"]
    ]

    grupo_b = historias_internacionales[
        relacion["grupo_b"]
    ]

    conceptos = ", ".join(
        relacion["conceptos"]
    )

    print()
    print(
        f"Conceptos comunes: {conceptos}"
    )

    print(
        f"  A: {grupo_a['titulo']}"
    )

    print(
        f"  B: {grupo_b['titulo']}"
    )

print()
print("=" * 80)
print("8. COMPARANDO INTERNACIONAL VS ESPAÑA")
print("=" * 80)


comparaciones = comparar_internacional_espana(
    historias_internacionales,
    historias_espana
)


print(
    "Comparaciones/señales detectadas:",
    len(comparaciones)
)

print()
print("=" * 80)
print("DETALLE DE LAS HISTORIAS CON MAYOR BRECHA")
print("=" * 80)

for comparacion in comparaciones:

    if comparacion["espana"] is not None:
        continue

    if comparacion["fuentes_internacionales"] < 2:
        continue

    historia = comparacion["internacional"]

    print()
    print(
        f"Título: {historia['titulo']}"
    )

    print(
        f"Publicaciones: {historia['publicaciones']}"
    )

    print(
        f"Fuentes: {historia['fuentes']}"
    )

    print(
        "Noticias que forman la historia:"
    )

    for noticia in historia["noticias"]:
        print(
            f"  - {noticia['title']}"
        )


print()
print("=" * 80)
print("HISTORIAS INTERNACIONALES SIN EQUIVALENTE EN ESPAÑA")
print("=" * 80)


sin_equivalente = []

for comparacion in comparaciones:

    if comparacion["espana"] is not None:
        continue

    if comparacion["fuentes_internacionales"] < 2:
        continue

    brecha = calcular_brecha_internacional_espana(
        comparacion
    )

    historia = comparacion["internacional"]

    sin_equivalente.append(
        (
            brecha["brecha_publicaciones"],
            brecha["brecha_fuentes"],
            historia["titulo"],
        )
    )


sin_equivalente.sort(
    key=lambda x: (x[0], x[1]),
    reverse=True
)


print()
print("=" * 80)
print("TOP 15 HISTORIAS CON MAYOR BRECHA")
print("=" * 80)


for numero, (
    publicaciones,
    fuentes,
    titulo
) in enumerate(
    sin_equivalente[:15],
    start=1
):

    print()
    print(
        f"{numero:>2}. "
        f"Publicaciones: {publicaciones} | "
        f"Fuentes: {fuentes}"
    )

    print(
        f"    {titulo}"
    )