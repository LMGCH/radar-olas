from radar import (
    buscar_noticias,
    buscar_noticias_internacionales,
)

from filtro import filtrar_noticias
from agrupador import agrupar_noticias, palabras_clave
from senales import CONCEPTOS_GENERALES_COMPARACION


TEMA = "OpenAI"
HORAS = 24

MAX_FRECUENCIA = 3


def obtener_conceptos(historias):
    resultado = []

    for historia in historias:
        conceptos = (
            palabras_clave(historia["titulo"])
            - CONCEPTOS_GENERALES_COMPARACION
        )
        resultado.append(conceptos)

    return resultado


def contar_frecuencias(conceptos_por_historia):
    frecuencias = {}

    for conceptos in conceptos_por_historia:
        for concepto in conceptos:
            frecuencias[concepto] = (
                frecuencias.get(concepto, 0) + 1
            )

    return frecuencias


print("=" * 70)
print(" PRUEBA FINAL DE COMPARACIÓN")
print("=" * 70)

# ------------------------------------------------------------
# INTERNACIONAL
# ------------------------------------------------------------

noticias_internacionales, tema_internacional = (
    buscar_noticias_internacionales(
        TEMA,
        horas=HORAS
    )
)

relevantes_internacionales, _ = filtrar_noticias(
    noticias_internacionales,
    tema_internacional
)

historias_internacionales = agrupar_noticias(
    relevantes_internacionales,
    tema=tema_internacional
)

# ------------------------------------------------------------
# ESPAÑOL
# ------------------------------------------------------------

noticias_espana = buscar_noticias(
    TEMA,
    horas=HORAS
)

relevantes_espana, _ = filtrar_noticias(
    noticias_espana,
    TEMA
)

historias_espana = agrupar_noticias(
    relevantes_espana,
    tema=TEMA
)

# ------------------------------------------------------------
# FRECUENCIAS
# ------------------------------------------------------------

conceptos_historias_int = obtener_conceptos(
    historias_internacionales
)

conceptos_historias_es = obtener_conceptos(
    historias_espana
)

frecuencias_int = contar_frecuencias(
    conceptos_historias_int
)

frecuencias_es = contar_frecuencias(
    conceptos_historias_es
)

# ------------------------------------------------------------
# COMPARACIÓN
# ------------------------------------------------------------

coincidencias = []

for historia_int, conceptos_int_historia in zip(
    historias_internacionales,
    conceptos_historias_int
):
    for historia_es, conceptos_es_historia in zip(
        historias_espana,
        conceptos_historias_es
    ):
        comunes = (
            conceptos_int_historia
            & conceptos_es_historia
        )

        if len(comunes) < 2:
            continue

        conceptos_distintivos = [
            concepto
            for concepto in comunes
            if frecuencias_int.get(concepto, 0) <= MAX_FRECUENCIA
            and frecuencias_es.get(concepto, 0) <= MAX_FRECUENCIA
        ]

        if not conceptos_distintivos:
            continue

        coincidencias.append(
            (
                historia_int,
                historia_es,
                sorted(comunes),
                sorted(conceptos_distintivos),
            )
        )

# ------------------------------------------------------------
# RESULTADOS
# ------------------------------------------------------------

print(
    f"\nHistorias internacionales: "
    f"{len(historias_internacionales)}"
)

print(
    f"Historias español: "
    f"{len(historias_espana)}"
)

print(
    f"\nFrecuencia máxima para considerar "
    f"un concepto distintivo: {MAX_FRECUENCIA}"
)

print(
    f"\nCoincidencias encontradas: "
    f"{len(coincidencias)}"
)

print("\n" + "-" * 70)

for numero, (
    internacional,
    espana,
    comunes,
    distintivos,
) in enumerate(coincidencias, 1):

    print(f"\n{numero:02d}")
    print(f"INT: {internacional['titulo']}")
    print(f"ES : {espana['titulo']}")
    print(f"Comunes: {comunes}")
    print(f"Distintivos: {distintivos}")

print("\n" + "=" * 70)
print(" FIN DE LA PRUEBA FINAL")
print("=" * 70)