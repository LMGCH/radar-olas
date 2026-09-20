from datetime import datetime, timezone

from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias
from velocidad import analizar_historia_temporal


TEMA = "robotics"
HORAS = 24

noticias = buscar_noticias(
    TEMA,
    horas=HORAS
)

relevantes, _ = filtrar_noticias(
    noticias,
    TEMA
)

grupos = agrupar_noticias(
    relevantes
)

ahora = datetime.now(timezone.utc)

print()
print("==============================")
print(" PRUEBA ANÁLISIS DE HISTORIA")
print("==============================")

for numero, grupo in enumerate(grupos, start=1):

    resultado = analizar_historia_temporal(
        grupo,
        ahora
    )

    if resultado is None:
        continue

    print()
    print(f"--- Historia {numero} ---")
    print(grupo["titulo"])

    print(
        "Publicaciones:",
        len(grupo["noticias"])
    )

    print(
        "Fuentes:",
        grupo["fuentes"]
    )

    print(
        "Velocidad:",
        resultado["etiqueta_velocidad"]
    )

    print(
        "Estado reciente:",
        resultado["estado_reciente"]
    )

    print(
        "Difusión:",
        resultado["difusion"]
    )

    print(
        "Patrón:",
        resultado["patron_temporal"]
    )

    print(
        "Interpretación:",
        resultado["interpretacion"]
    )