from radar import (
    buscar_noticias,
    buscar_noticias_internacionales,
)

from senales import (
    comparar_internacional_espana,
    calcular_brecha_internacional_espana,
)

from filtro import filtrar_noticias
from agrupador import agrupar_noticias


TEMA = "robotics"

HORAS = 24

from agrupador import palabras_clave

from senales import CONCEPTOS_GENERALES_COMPARACION


print("\n==============================")
print(" PRUEBA COMPARACIÓN INTERNACIONAL / ESPAÑA")
print("==============================\n")


# Buscar noticias
noticias_internacionales, tema_internacional = (
    buscar_noticias_internacionales(
        TEMA,
        horas=HORAS
    )
)

noticias_espana = buscar_noticias(
    TEMA,
    horas=HORAS
)


print(
    "Consulta internacional:",
    tema_internacional
)


# Filtrar
relevantes_internacionales, _ = filtrar_noticias(
    noticias_internacionales,
    tema_internacional
)

relevantes_espana, _ = filtrar_noticias(
    noticias_espana,
    TEMA
)


# Agrupar
historias_internacionales = agrupar_noticias(
    relevantes_internacionales,
    tema=tema_internacional
)

historias_espana = agrupar_noticias(
    relevantes_espana,
    tema=TEMA
)

print("\n==============================")
print(" HISTORIAS ESPAÑA")
print("==============================\n")

for numero, historia in enumerate(
    historias_espana,
    start=1
):
    print(f"--- España {numero} ---")
    print("Título:", historia["titulo"])
    print(
        "Publicaciones:",
        historia["publicaciones"],
        "/ Fuentes:",
        historia["fuentes"]
    )
    print()

# Comparar
comparaciones = comparar_internacional_espana(
    historias_internacionales,
    historias_espana
)


print(
    f"\nNoticias internacionales: "
    f"{len(noticias_internacionales)}"
)

print(
    f"Historias internacionales: "
    f"{len(historias_internacionales)}"
)

print(
    f"Noticias España: "
    f"{len(noticias_espana)}"
)

print(
    f"Historias España: "
    f"{len(historias_espana)}"
)

print(
    f"\nComparaciones encontradas: "
    f"{len(comparaciones)}\n"
)


for numero, comparacion in enumerate(
    comparaciones,
    start=1
):

    historia_int = comparacion["internacional"]
    historia_es = comparacion["espana"]

    brecha = calcular_brecha_internacional_espana(
        comparacion
    )

    print(f"--- Comparación {numero} ---")

    print(
        "Internacional:",
        historia_int["titulo"]
    )

    if historia_es:
        print(
            "España:",
            historia_es["titulo"]
        )
    else:
        print(
            "España: SIN EQUIVALENTE"
        )

    print(
        "Conceptos comunes:",
        ", ".join(
            comparacion["conceptos_comunes"]
        )
        if comparacion["conceptos_comunes"]
        else "ninguno"
    )

    print(
        "Internacional:",
        comparacion["publicaciones_internacionales"],
        "publicaciones /",
        comparacion["fuentes_internacionales"],
        "fuentes"
    )

    print(
        "España:",
        comparacion["publicaciones_espana"],
        "publicaciones /",
        comparacion["fuentes_espana"],
        "fuentes"
    )

    print(
        "Brecha publicaciones:",
        brecha["brecha_publicaciones"]
    )

    print(
        "Brecha fuentes:",
        brecha["brecha_fuentes"]
    )

    print()

    print("\n==============================")
    print(" CONCEPTOS GENERALES EXCLUIDOS")
    print("==============================\n")

    print(
        sorted(CONCEPTOS_GENERALES_COMPARACION)
    )

    print("\n==============================")
    print(" CONCEPTOS DE LAS HISTORIAS")
    print("==============================\n")

    for numero, historia in enumerate(
        historias_espana,
        start=1
    ):
        conceptos = palabras_clave(
            historia["titulo"]
        )

        print(
            f"España {numero}:",
            historia["titulo"]
        )
        print(
            "Conceptos:",
            sorted(conceptos)
        )
        print()
