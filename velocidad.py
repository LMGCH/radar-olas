from datetime import datetime, timezone, timedelta

from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias


VENTANA_RECIENTE_HORAS = 2
VENTANA_ANTERIOR_HORAS = 2
VENTANA_TOTAL_HORAS = 24
INTERVALO_HORAS = 2


def obtener_fecha(noticia):
    """
    Devuelve la fecha de publicación de una noticia.
    """

    return noticia.get("datetime")


def obtener_noticias_en_ventana(noticias, inicio, fin):
    """
    Devuelve las noticias cuya fecha está dentro de la ventana.
    """

    resultado = []

    for noticia in noticias:

        fecha = obtener_fecha(noticia)

        if fecha is None:
            continue

        if inicio <= fecha < fin:
            resultado.append(noticia)

    return resultado


def calcular_velocidad(noticias, horas):
    """
    Calcula publicaciones por hora.
    """

    if horas <= 0:
        return 0

    return len(noticias) / horas


def calcular_fuentes(noticias):
    """
    Calcula el número de fuentes diferentes.
    """

    return len(
        {
            noticia.get("domain", "Desconocida")
            for noticia in noticias
        }
    )


def calcular_factor_aceleracion(
    velocidad_reciente,
    velocidad_anterior
):
    """
    Compara la velocidad reciente con la anterior.

    Si no existe actividad anterior pero sí reciente,
    se considera una aparición nueva.

    Si no existe actividad en ninguno de los dos periodos,
    no existe aceleración medible.
    """

    if velocidad_anterior == 0:

        if velocidad_reciente > 0:
            return None

        return None

    return velocidad_reciente / velocidad_anterior


def interpretar_velocidad(
    velocidad_reciente,
    velocidad_anterior,
    factor
):
    """
    Interpreta exclusivamente la comparación
    entre los dos últimos periodos.
    """

    if velocidad_anterior == 0:

        if velocidad_reciente > 0:
            return "🆕 Aparición reciente"

        return "⏸️ Sin actividad reciente"

    if factor >= 2:
        return "🔥 Aceleración"

    if factor > 1:
        return "📈 Aumento de velocidad"

    if factor == 1:
        return "➡️ Velocidad estable"

    return "📉 Desaceleración"


def interpretar_estado_reciente(
    publicaciones_recientes,
    fuentes_recientes
):
    """
    Describe el estado de la actividad reciente.
    """

    if publicaciones_recientes == 0:
        return "⏸️ Sin actividad reciente"

    if publicaciones_recientes >= 3 and fuentes_recientes >= 3:
        return "🔥 Actividad intensa"

    if publicaciones_recientes >= 2 and fuentes_recientes >= 2:
        return "📈 Movimiento"

    if publicaciones_recientes >= 2:
        return "📢 Amplificación"

    return "🌱 Señal inicial"


def interpretar_difusion(
    publicaciones,
    fuentes
):
    """
    Describe cómo se distribuye la historia entre fuentes.
    """

    if publicaciones == 1:
        return "🌱 Señal aislada"

    if fuentes >= 3:
        return "🌐 Propagación"

    if fuentes >= 2:
        return "🌐 Difusión"

    return "📢 Concentración en una fuente"

def clasificar_patron_temporal(
    publicaciones,
    periodos_activos,
    pico_actividad,
    reaparicion,
    velocidad_reciente,
    velocidad_anterior,
):
    """
    Clasifica el comportamiento temporal observado
    sin realizar predicciones.
    """

    if publicaciones <= 1:
        return "🌱 Señal aislada"

    if reaparicion:
        return "🔄 Reaparición"

    if velocidad_anterior > 0 and velocidad_reciente > velocidad_anterior:
        return "📈 Aumento de actividad"

    if periodos_activos >= 3 and pico_actividad >= 2:
        return "➡️ Actividad sostenida"
    
    if periodos_activos == 1:
        return "⚡ Concentración temporal"

    if periodos_activos >= 2:
        return "🌐 Expansión temporal"

    return "📢 Concentración temporal"

def interpretar_historia(
    publicaciones,
    fuentes,
    etiqueta_velocidad,
    difusion,
    patron_temporal,
):
    """
    Genera una interpretación breve y explicable
    a partir de las señales ya calculadas.

    No realiza predicciones.
    """

    if publicaciones <= 1:
        return "🌱 Primera señal detectada."

    if patron_temporal == "🔄 Reaparición":

        if fuentes > 1:
            return (
                "🔄 La historia reaparece después de un periodo "
                "sin actividad y ya aparece en varias fuentes."
            )

        return (
            "🔄 La historia reaparece después de un periodo "
            "sin actividad."
        )

    if etiqueta_velocidad == "🔥 Aceleración":

        if fuentes > 1:
            return (
                "🔥 La actividad está aumentando respecto "
                "al periodo anterior y se observa en varias fuentes."
            )

        return (
            "🔥 La actividad está aumentando respecto "
            "al periodo anterior."
        )

    if patron_temporal == "➡️ Actividad sostenida":

        if fuentes > 1:
            return (
                "➡️ La historia mantiene actividad en varios "
                "periodos y aparece en varias fuentes."
            )

        return (
            "➡️ La historia mantiene actividad "
            "en varios periodos."
        )

    if patron_temporal == "🌐 Expansión temporal":

        if fuentes > 1:
            return (
                "🌐 La historia aparece en varios periodos "
                "y se difunde entre varias fuentes."
            )

        return (
            "🌐 La historia aparece en varios periodos "
            "de tiempo."
        )

    if patron_temporal == "⚡ Concentración temporal":

        if fuentes > 1:
            return (
                "⚡ Varias publicaciones se concentran "
                "en un mismo periodo y proceden de varias fuentes."
            )

        return (
            "⚡ Varias publicaciones se concentran "
            "en un mismo periodo."
        )

    if fuentes > 1:
        return (
            "📡 Hay actividad detectada y difusión entre "
            "varias fuentes, pero todavía no muestra un "
            "patrón temporal definido."
        )

    return (
        "📡 Hay actividad detectada, pero todavía "
        "no muestra un patrón temporal definido."
    )

def analizar_evolucion_temporal(
    noticias,
    ahora
):
    """
    Divide las últimas 24 horas en periodos de 2 horas
    y analiza la evolución temporal de una historia.

    Además de la actividad de cada periodo, calcula:

    - actividad total
    - número de periodos activos
    - pico de publicaciones
    - periodo del pico
    - reaparición después de un periodo sin actividad
    """

    periodos = []

    inicio_total = ahora - timedelta(
        hours=VENTANA_TOTAL_HORAS
    )

    for indice in range(
        0,
        VENTANA_TOTAL_HORAS,
        INTERVALO_HORAS
    ):

        inicio = inicio_total + timedelta(
            hours=indice
        )

        fin = inicio + timedelta(
            hours=INTERVALO_HORAS
        )

        noticias_periodo = obtener_noticias_en_ventana(
            noticias,
            inicio,
            fin
        )

        publicaciones = len(noticias_periodo)

        fuentes = calcular_fuentes(
            noticias_periodo
        )

        periodos.append(
            {
                "inicio": inicio,
                "fin": fin,
                "publicaciones": publicaciones,
                "fuentes": fuentes,
            }
        )

    actividad_total = sum(
        periodo["publicaciones"]
        for periodo in periodos
    )

    periodos_activos = sum(
        1
        for periodo in periodos
        if periodo["publicaciones"] > 0
    )

    pico_publicaciones = max(
        (
            periodo["publicaciones"]
            for periodo in periodos
        ),
        default=0
    )

    periodos_pico = [
        indice
        for indice, periodo in enumerate(periodos)
        if periodo["publicaciones"] == pico_publicaciones
        and pico_publicaciones > 0
    ]

    reaparicion = False

    hubo_actividad = False
    hubo_inactividad = False

    for periodo in periodos:

        publicaciones = periodo["publicaciones"]

        if publicaciones > 0:

            if hubo_inactividad and hubo_actividad:
                reaparicion = True

            hubo_actividad = True

        else:

            if hubo_actividad:
                hubo_inactividad = True

    return {
        "periodos": periodos,
        "actividad_total_24h": actividad_total,
        "periodos_activos": periodos_activos,
        "pico_publicaciones": pico_publicaciones,
        "periodos_pico": periodos_pico,
        "reaparicion": reaparicion,
    }

def analizar_historia_temporal(
    grupo,
    ahora
):
    """
    Analiza temporalmente una historia ya agrupada.

    No realiza ninguna búsqueda.
    Recibe una historia y devuelve sus señales temporales.
    """

    publicaciones = grupo["noticias"]

    fechas_grupo = [
        obtener_fecha(noticia)
        for noticia in publicaciones
        if obtener_fecha(noticia) is not None
    ]

    if not fechas_grupo:
        return None

    primera_aparicion = min(fechas_grupo)
    ultima_aparicion = max(fechas_grupo)

    duracion = (
        ultima_aparicion
        - primera_aparicion
    ).total_seconds() / 3600

    if duracion <= 0:
        duracion = None

    if duracion is None:
        velocidad_acumulada = None
    else:
        velocidad_acumulada = (
            len(publicaciones)
            / duracion
        )

    inicio_ventana_anterior = (
        ahora
        - timedelta(
            hours=VENTANA_ANTERIOR_HORAS
        )
    )

    inicio_ventana_reciente = (
        ahora
        - timedelta(
            hours=VENTANA_RECIENTE_HORAS
        )
    )

    noticias_anteriores = obtener_noticias_en_ventana(
        publicaciones,
        inicio_ventana_anterior,
        inicio_ventana_reciente
    )

    noticias_recientes = obtener_noticias_en_ventana(
        publicaciones,
        inicio_ventana_reciente,
        ahora
    )

    publicaciones_anteriores = len(
        noticias_anteriores
    )

    publicaciones_recientes = len(
        noticias_recientes
    )

    fuentes_anteriores = calcular_fuentes(
        noticias_anteriores
    )

    fuentes_recientes = calcular_fuentes(
        noticias_recientes
    )

    velocidad_anterior = calcular_velocidad(
        noticias_anteriores,
        VENTANA_ANTERIOR_HORAS
    )

    velocidad_reciente = calcular_velocidad(
        noticias_recientes,
        VENTANA_RECIENTE_HORAS
    )

    factor = calcular_factor_aceleracion(
        velocidad_reciente,
        velocidad_anterior
    )

    etiqueta_velocidad = interpretar_velocidad(
        velocidad_reciente,
        velocidad_anterior,
        factor
    )

    estado_reciente = interpretar_estado_reciente(
        publicaciones_recientes,
        fuentes_recientes
    )

    difusion = interpretar_difusion(
        len(publicaciones),
        grupo["fuentes"]
    )

    horas_desde_ultima = (
        ahora - ultima_aparicion
    ).total_seconds() / 3600

    evolucion = analizar_evolucion_temporal(
        publicaciones,
        ahora
    )

    patron_temporal = clasificar_patron_temporal(
        len(publicaciones),
        evolucion["periodos_activos"],
        evolucion["pico_publicaciones"],
        evolucion["reaparicion"],
        velocidad_reciente,
        velocidad_anterior,
    )

    interpretacion = interpretar_historia(
        len(publicaciones),
        grupo["fuentes"],
        etiqueta_velocidad,
        difusion,
        patron_temporal,
    )

    return {
        "primera_aparicion": primera_aparicion,
        "ultima_aparicion": ultima_aparicion,
        "duracion": duracion,
        "velocidad_acumulada": velocidad_acumulada,
        "publicaciones_anteriores": publicaciones_anteriores,
        "publicaciones_recientes": publicaciones_recientes,
        "fuentes_anteriores": fuentes_anteriores,
        "fuentes_recientes": fuentes_recientes,
        "velocidad_anterior": velocidad_anterior,
        "velocidad_reciente": velocidad_reciente,
        "factor": factor,
        "etiqueta_velocidad": etiqueta_velocidad,
        "estado_reciente": estado_reciente,
        "difusion": difusion,
        "horas_desde_ultima": horas_desde_ultima,
        "evolucion": evolucion,
        "patron_temporal": patron_temporal,
        "interpretacion": interpretacion,
    }

def analizar_velocidad(noticias, tema):
    """
    Ejecuta el análisis temporal completo.
    """

    print("=" * 80)
    print("ANÁLISIS TEMPORAL")
    print("=" * 80)

    relevantes, descartadas = filtrar_noticias(
        noticias,
        tema
    )

    grupos = agrupar_noticias(
        relevantes
    )

    print(
        f"Noticias recibidas: {len(noticias)}"
    )

    print(
        f"Noticias relevantes: {len(relevantes)}"
    )

    print(
        f"Historias detectadas: {len(grupos)}"
    )

    if not relevantes:
        print()
        print("No se encontraron noticias relevantes.")
        return []

    fechas = [
        obtener_fecha(noticia)
        for noticia in relevantes
        if obtener_fecha(noticia) is not None
    ]

    if not fechas:
        print()
        print("No hay fechas válidas para realizar el análisis.")
        return []

    ahora = datetime.now(timezone.utc)


    print()
    print("Analizando evolución temporal...")

    inicio_ventana_anterior = (
        ahora
        - timedelta(
            hours=VENTANA_ANTERIOR_HORAS
        )
    )

    inicio_ventana_reciente = (
        ahora
        - timedelta(
            hours=VENTANA_RECIENTE_HORAS
        )
    )
    resultados = []

    for indice, grupo in enumerate(grupos, start=1):

        publicaciones = grupo["noticias"]


        fechas_grupo = [
            obtener_fecha(noticia)
            for noticia in publicaciones
            if obtener_fecha(noticia) is not None
        ]

        if not fechas_grupo:
            continue

        primera_aparicion = min(fechas_grupo)
        ultima_aparicion = max(fechas_grupo)

        duracion = (
            ultima_aparicion
            - primera_aparicion
        ).total_seconds() / 3600

        if duracion <= 0:
            duracion = None

        if duracion is None:
            velocidad_acumulada = None
        else:
            velocidad_acumulada = (
                len(publicaciones)
                / duracion
            )

        noticias_anteriores = obtener_noticias_en_ventana(
            publicaciones,
            inicio_ventana_anterior,
            inicio_ventana_reciente
        )

        noticias_recientes = obtener_noticias_en_ventana(
            publicaciones,
            inicio_ventana_reciente,
            ahora
        )

        publicaciones_anteriores = len(
            noticias_anteriores
        )

        publicaciones_recientes = len(
            noticias_recientes
        )

        fuentes_anteriores = calcular_fuentes(
            noticias_anteriores
        )

        fuentes_recientes = calcular_fuentes(
            noticias_recientes
        )

        velocidad_anterior = calcular_velocidad(
            noticias_anteriores,
            VENTANA_ANTERIOR_HORAS
        )

        velocidad_reciente = calcular_velocidad(
            noticias_recientes,
            VENTANA_RECIENTE_HORAS
        )

        factor = calcular_factor_aceleracion(
            velocidad_reciente,
            velocidad_anterior
        )

        etiqueta_velocidad = interpretar_velocidad(
            velocidad_reciente,
            velocidad_anterior,
            factor
        )

        estado_reciente = interpretar_estado_reciente(
            publicaciones_recientes,
            fuentes_recientes
        )

        difusion = interpretar_difusion(
            len(publicaciones),
            grupo["fuentes"]
        )

        horas_desde_ultima = (
            ahora - ultima_aparicion
        ).total_seconds() / 3600

        evolucion = analizar_evolucion_temporal(
            publicaciones,
            ahora
        )
        patron_temporal = clasificar_patron_temporal(
            len(publicaciones),
            evolucion["periodos_activos"],
            evolucion["pico_publicaciones"],
            evolucion["reaparicion"],
            velocidad_reciente,
            velocidad_anterior,
        )

        resultados.append(
            {
                "historia": grupo,
                "publicaciones": len(publicaciones),
                "fuentes": grupo["fuentes"],
                "publicaciones_anteriores": publicaciones_anteriores,
                "publicaciones_recientes": publicaciones_recientes,
                "fuentes_anteriores": fuentes_anteriores,
                "fuentes_recientes": fuentes_recientes,
                "velocidad_anterior": velocidad_anterior,
                "velocidad_reciente": velocidad_reciente,
                "factor": factor,
                "etiqueta_velocidad": etiqueta_velocidad,
                "estado_reciente": estado_reciente,
                "difusion": difusion,
                "horas_desde_ultima": horas_desde_ultima,
                "evolucion": evolucion,
                "patron_temporal": patron_temporal,
            }
        )

    return resultados

def seleccionar_candidatas(resultados, limite=5):
    """
    Selecciona historias que muestran indicios suficientes
    de expansión reciente.

    No determina si una historia merece publicarse.
    Solo reduce el universo de historias a un pequeño grupo
    que merece revisión editorial humana.

    Una señal aislada no se considera candidata.
    Se requiere al menos una evidencia adicional de expansión:
    - varias publicaciones recientes, o
    - varias fuentes recientes.
    """

    candidatas = []

    for resultado in resultados:

        publicaciones_recientes = (
            resultado["publicaciones_recientes"]
        )

        fuentes_recientes = (
            resultado["fuentes_recientes"]
        )

        horas_desde_ultima = (
            resultado["horas_desde_ultima"]
        )

        velocidad_reciente = (
            resultado["velocidad_reciente"]
        )

        velocidad_anterior = (
            resultado["velocidad_anterior"]
        )

        periodos_activos = (
            resultado["evolucion"]["periodos_activos"]
        )

        if publicaciones_recientes == 0:

            continue

        if fuentes_recientes == 0:

            continue
   

        # Una publicación reciente por sí sola es una señal.
        # Para convertirse en candidata debe existir además
        # alguna evidencia de continuidad o difusión.
        hay_difusion_reciente = (
            publicaciones_recientes >= 2
            or fuentes_recientes >= 2
        )

        hay_continuidad = (
            periodos_activos >= 2
        )

        hay_traccion_historica = (
            resultado["publicaciones"] >= 3
            or resultado["fuentes"] >= 2
        )

        if not (
            hay_difusion_reciente
            or (hay_continuidad and hay_traccion_historica)
        ):
            print(
                f"DESCARTADA poca expansión: "
                f"{resultado['historia']['titulo']}"
            )
            continue

        puntos = 0

        # Actividad reciente
        if publicaciones_recientes >= 3:
            puntos += 2
        else:
            puntos += 1

        # Difusión entre fuentes
        if fuentes_recientes >= 3:
            puntos += 2
        else:
            puntos += 1

        # Aparición o aceleración reciente
        if (
            velocidad_anterior == 0
            and velocidad_reciente > 0
        ):
            puntos += 2

        elif (
            velocidad_anterior > 0
            and velocidad_reciente > velocidad_anterior
        ):
            puntos += 2

        # Frescura
        if horas_desde_ultima <= 1:
            puntos += 2

        elif horas_desde_ultima <= 2:
            puntos += 1

        # Expansión temporal
        if periodos_activos >= 2:
            puntos += 1

        candidatas.append(
            {
                **resultado,
                "puntos_selector": puntos,
            }
        )

    candidatas.sort(
        key=lambda resultado: (
            resultado["puntos_selector"],
            resultado["publicaciones_recientes"],
            resultado["fuentes_recientes"],
            resultado["velocidad_reciente"],
            -resultado["horas_desde_ultima"],
        ),
        reverse=True,
    )

    return candidatas[:limite]

if __name__ == "__main__":

    tema = input("Tema: ").strip()

    resultados = analizar_velocidad(tema)

    candidatas = seleccionar_candidatas(resultados)

    print()
    print("=" * 80)
    print("CANDIDATAS DETECTADAS")
    print("=" * 80)

    if not candidatas:

        print("No se han detectado candidatas.")

    else:

        for candidata in candidatas:

            print(
                f"- {candidata['historia']['titulo']}"
            )

            print(
                f"  Puntos selector: "
                f"{candidata['puntos_selector']}"
            )

            print(
                f"  Recientes: "
                f"{candidata['publicaciones_recientes']} publicaciones · "
                f"{candidata['fuentes_recientes']} fuentes"
            )

            print(
                f"  Última publicación hace: "
                f"{candidata['horas_desde_ultima']:.2f} h"
            )