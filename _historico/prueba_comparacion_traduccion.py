from radar import (
    buscar_noticias,
    buscar_noticias_internacionales,
)

from filtro import filtrar_noticias
from agrupador import agrupar_noticias, palabras_clave
from senales import CONCEPTOS_GENERALES_COMPARACION


TEMA = "OpenAI"
HORAS = 24


def traducir_concepto(concepto):
    """
    Traduce un concepto del inglés al español usando Argos Translate.
    """
    try:
        import argostranslate.translate as translate

        traduccion = translate.translate(
            concepto,
            "en",
            "es"
        )

        return traduccion.strip().lower()

    except Exception:
        return concepto.lower()


def obtener_conceptos_traducidos(titulo):
    """
    Extrae conceptos del titular internacional y traduce
    cada concepto individualmente al español.
    """
    conceptos = palabras_clave(titulo)

    resultado = set()

    for concepto in conceptos:

        traduccion = traducir_concepto(
            concepto
        )

        if traduccion:
            resultado.add(traduccion)

    return resultado


print()
print("=" * 70)
print(" PRUEBA COMPARACIÓN INTERNACIONAL / ESPAÑOL")
print(" CONCEPTOS TRADUCIDOS CON ARGOS")
print("=" * 70)
print()

print(f"Tema: {TEMA}")
print(f"Ventana: {HORAS} horas")
print()


# ============================================================
# 1. BUSCAR
# ============================================================

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
    f"Consulta internacional: "
    f"{tema_internacional}"
)

print()


# ============================================================
# 2. FILTRAR
# ============================================================

relevantes_internacionales, _ = (
    filtrar_noticias(
        noticias_internacionales,
        tema_internacional
    )
)

relevantes_espana, _ = (
    filtrar_noticias(
        noticias_espana,
        TEMA
    )
)


print(
    f"Noticias internacionales relevantes: "
    f"{len(relevantes_internacionales)}"
)

print(
    f"Noticias españolas relevantes: "
    f"{len(relevantes_espana)}"
)

print()


# ============================================================
# 3. AGRUPAR
# ============================================================

historias_internacionales = agrupar_noticias(
    relevantes_internacionales,
    tema=tema_internacional
)

historias_espana = agrupar_noticias(
    relevantes_espana,
    tema=TEMA
)


print(
    f"Historias internacionales: "
    f"{len(historias_internacionales)}"
)

print(
    f"Historias españolas: "
    f"{len(historias_espana)}"
)

print()


# ============================================================
# 4. COMPARACIÓN
# ============================================================

coincidencias = []


for historia_int in historias_internacionales:

    titulo_int = historia_int["titulo"]

    conceptos_int = palabras_clave(
        titulo_int
    )

    conceptos_int_traducidos = (
        obtener_conceptos_traducidos(
            titulo_int
        )
    )

    # Quitamos los conceptos generales del tema.
    conceptos_int_traducidos -= (
        CONCEPTOS_GENERALES_COMPARACION
    )

    for historia_es in historias_espana:

        titulo_es = historia_es["titulo"]

        conceptos_es = palabras_clave(
            titulo_es
        )

        conceptos_es -= (
            CONCEPTOS_GENERALES_COMPARACION
        )

        comunes = (
            conceptos_int_traducidos
            & conceptos_es
        )

        if len(comunes) < 2:
            continue

        coincidencias.append(
            {
                "internacional": historia_int,
                "espanol": historia_es,
                "conceptos_originales": sorted(
                    conceptos_int
                ),
                "conceptos_traducidos": sorted(
                    conceptos_int_traducidos
                ),
                "conceptos_espanol": sorted(
                    conceptos_es
                ),
                "comunes": sorted(
                    comunes
                ),
            }
        )


# ============================================================
# 5. RESULTADOS
# ============================================================

print("=" * 70)
print(" POSIBLES COINCIDENCIAS")
print("=" * 70)
print()


if not coincidencias:

    print(
        "No se encontraron coincidencias "
        "con al menos 2 conceptos específicos."
    )

else:

    for numero, coincidencia in enumerate(
        coincidencias,
        start=1
    ):

        internacional = (
            coincidencia["internacional"]
        )

        espanol = (
            coincidencia["espanol"]
        )

        print(
            f"{numero:02d}. POSIBLE COINCIDENCIA"
        )

        print()
        print("  🌍 Internacional:")
        print(
            f"     {internacional['titulo']}"
        )

        print(
            f"     {internacional['publicaciones']} "
            f"publicaciones · "
            f"{internacional['fuentes']} fuentes"
        )

        print()

        print("  🇪🇸 Español:")
        print(
            f"     {espanol['titulo']}"
        )

        print(
            f"     {espanol['publicaciones']} "
            f"publicaciones · "
            f"{espanol['fuentes']} fuentes"
        )

        print()

        print("  Conceptos originales:")
        print(
            f"     "
            f"{coincidencia['conceptos_originales']}"
        )

        print()

        print("  Conceptos traducidos:")
        print(
            f"     "
            f"{coincidencia['conceptos_traducidos']}"
        )

        print()

        print("  Conceptos de la historia española:")
        print(
            f"     "
            f"{coincidencia['conceptos_espanol']}"
        )

        print()

        print("  ✅ Conceptos comunes:")
        print(
            f"     "
            f"{coincidencia['comunes']}"
        )

        print()
        print("-" * 70)
        print()


print(
    f"Total de posibles coincidencias: "
    f"{len(coincidencias)}"
)

print()
print("=" * 70)
print(" FIN DE LA PRUEBA")
print("=" * 70)


