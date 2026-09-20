from agrupador import palabras_clave


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


CONCEPTOS_GENERALES_COMPARACION = {
    "robot",
    "robots",
    "robotics",
    "digital",
    "technology",
    "technologies",
    "tecnologia",
    "tecnologias",
    "innovation",
    "innovacion",
    "artificial",
    "intelligence",
    "inteligencia",
}


def conceptos(titulo):
    """
    Extrae conceptos de un titular eliminando palabras de ruido.
    """

    palabras = palabras_clave(titulo)

    return {
        palabra
        for palabra in palabras
        if palabra not in PALABRAS_RUIDO
    }


def relacion(grupo_a, grupo_b):
    """
    Obtiene los conceptos compartidos entre dos historias.
    """

    conceptos_a = conceptos(
        grupo_a["titulo"]
    )

    conceptos_b = conceptos(
        grupo_b["titulo"]
    )

    return conceptos_a & conceptos_b


def detectar_relaciones(grupos):
    """
    Detecta relaciones entre historias que comparten
    al menos dos conceptos.
    """

    relaciones = []

    for i in range(len(grupos)):

        for j in range(i + 1, len(grupos)):

            comunes = relacion(
                grupos[i],
                grupos[j]
            )

            if len(comunes) < 2:
                continue

            relaciones.append(
                {
                    "grupo_a": i,
                    "grupo_b": j,
                    "conceptos": sorted(comunes),
                }
            )

    return relaciones


def comparar_internacional_espana(
    historias_internacionales,
    historias_espana,
):
    """
    Compara historias internacionales con historias de España.

    Busca coincidencias mediante conceptos compartidos.

    Se conservan también las historias internacionales que todavía
    no tienen equivalente en España.

    Una coincidencia requiere al menos dos conceptos comunes.

    Devuelve una lista de comparaciones.
    """

    comparaciones = []

    for historia_int in historias_internacionales:

        conceptos_int = (
            palabras_clave(historia_int["titulo"])
            - CONCEPTOS_GENERALES_COMPARACION
        )

        encontro_equivalente = False

        for historia_es in historias_espana:

            conceptos_es = (
                palabras_clave(historia_es["titulo"])
                - CONCEPTOS_GENERALES_COMPARACION
            )

            conceptos_comunes = (
                conceptos_int & conceptos_es
            )

            if len(conceptos_comunes) < 2:
                continue

            encontro_equivalente = True

            comparaciones.append(
                {
                    "internacional": historia_int,
                    "espana": historia_es,
                    "conceptos_comunes": sorted(
                        conceptos_comunes
                    ),
                    "publicaciones_internacionales": (
                        historia_int["publicaciones"]
                    ),
                    "fuentes_internacionales": (
                        historia_int["fuentes"]
                    ),
                    "publicaciones_espana": (
                        historia_es["publicaciones"]
                    ),
                    "fuentes_espana": (
                        historia_es["fuentes"]
                    ),
                }
            )

        if not encontro_equivalente:

            comparaciones.append(
                {
                    "internacional": historia_int,
                    "espana": None,
                    "conceptos_comunes": [],
                    "publicaciones_internacionales": (
                        historia_int["publicaciones"]
                    ),
                    "fuentes_internacionales": (
                        historia_int["fuentes"]
                    ),
                    "publicaciones_espana": 0,
                    "fuentes_espana": 0,
                }
            )

    return comparaciones


def calcular_brecha_internacional_espana(comparacion):
    """
    Calcula la diferencia de publicaciones y fuentes
    entre una historia internacional y su equivalente en España.
    """

    publicaciones_internacionales = (
        comparacion["publicaciones_internacionales"]
    )

    publicaciones_espana = (
        comparacion["publicaciones_espana"]
    )

    fuentes_internacionales = (
        comparacion["fuentes_internacionales"]
    )

    fuentes_espana = (
        comparacion["fuentes_espana"]
    )

    brecha_publicaciones = (
        publicaciones_internacionales
        - publicaciones_espana
    )

    brecha_fuentes = (
        fuentes_internacionales
        - fuentes_espana
    )

    return {
        "brecha_publicaciones": brecha_publicaciones,
        "brecha_fuentes": brecha_fuentes,
    }

