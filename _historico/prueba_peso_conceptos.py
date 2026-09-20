from radar import buscar_noticias, buscar_noticias_internacionales
from filtro import filtrar_noticias
from agrupador import agrupar_noticias, palabras_clave
from senales import CONCEPTOS_GENERALES_COMPARACION


TEMA = "OpenAI"
HORAS = 24


def extraer_conceptos(historias):
    conceptos = []

    for historia in historias:
        palabras = (
            palabras_clave(historia["titulo"])
            - CONCEPTOS_GENERALES_COMPARACION
        )
        conceptos.append(palabras)

    return conceptos


def contar_frecuencias(conceptos_por_historia):
    frecuencias = {}

    for conceptos in conceptos_por_historia:
        for concepto in conceptos:
            frecuencias[concepto] = frecuencias.get(concepto, 0) + 1

    return frecuencias


print("=" * 70)
print(" PRUEBA PESO DE CONCEPTOS")
print("=" * 70)

print(f"\nTema: {TEMA}")

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

conceptos_internacionales = extraer_conceptos(
    historias_internacionales
)

frecuencias_internacionales = contar_frecuencias(
    conceptos_internacionales
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

conceptos_espana = extraer_conceptos(
    historias_espana
)

frecuencias_espana = contar_frecuencias(
    conceptos_espana
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

print("\n" + "-" * 70)
print("CONCEPTOS INTERNACIONALES")
print("-" * 70)

for concepto, frecuencia in sorted(
    frecuencias_internacionales.items(),
    key=lambda x: (-x[1], x[0])
):
    print(f"{concepto:25} {frecuencia:3} historias")

print("\n" + "-" * 70)
print("CONCEPTOS ESPAÑOL")
print("-" * 70)

for concepto, frecuencia in sorted(
    frecuencias_espana.items(),
    key=lambda x: (-x[1], x[0])
):
    print(f"{concepto:25} {frecuencia:3} historias")

print("\n" + "=" * 70)
print(" FIN DE LA PRUEBA")
print("=" * 70)