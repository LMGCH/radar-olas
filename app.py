import streamlit as st

from datetime import timedelta

from radar import (

    buscar_noticias,

    buscar_noticias_internacionales,

    buscar_noticias_gdelt,

)

from tendencias import (
    obtener_tendencias_pais,
    obtener_tendencias_mundiales,
)

from filtro import filtrar_noticias

from agrupador import agrupar_noticias

from senales import (
    comparar_internacional_espana,
    calcular_brecha_internacional_espana,
)
from velocidad import analizar_velocidad, seleccionar_candidatas
from conceptos import detectar_conceptos_relacionados

st.set_page_config(

    page_title="Radar de Olas",

    page_icon="🌊",

    layout="wide"

)


VENTANA_RECIENTE_HORAS = 2
MAX_SENALES = 10


def calcular_tendencia(grupo):
    """
    Calcula una tendencia sencilla a partir de la actividad
    reciente de la historia.

    No mide crecimiento real entre periodos.
    Solo describe el movimiento observado dentro de la ventana.
    """

    noticias = grupo["noticias"]

    fechas = [
        noticia["datetime"]
        for noticia in noticias
        if noticia.get("datetime")
    ]

    if not fechas:
        return "🌱 Señal inicial:"

    referencia = max(fechas)

    limite = referencia - timedelta(
        hours=VENTANA_RECIENTE_HORAS
    )

    recientes = [
        noticia
        for noticia in noticias
        if (
            noticia.get("datetime")
            and noticia["datetime"] >= limite
        )
    ]

    fuentes_recientes = {
        noticia.get("domain", "Desconocida")
        for noticia in recientes
    }

    publicaciones_recientes = len(recientes)
    numero_fuentes = len(fuentes_recientes)

    if publicaciones_recientes >= 3 and numero_fuentes >= 3:
        return "🔥 Aceleración:"

    if publicaciones_recientes >= 2 and numero_fuentes >= 2:
        return "📈 Movimiento:"

    if publicaciones_recientes >= 2:
        return "📢 Amplificación:"

    return "🌱 Señal inicial:"


def calcular_difusion(grupo):
    """
    Describe cómo se distribuye una historia entre las fuentes.
    """

    publicaciones = grupo["publicaciones"]
    fuentes = grupo["fuentes"]

    if publicaciones == 1:
        return "🌱 Señal aislada:"

    if fuentes >= 3:
        return "🌐 Difusión entre fuentes:"

    if fuentes >= 2:
        return "🌐 Difusión:"

    return "📢 Concentración en una fuente:"


def preparar_senales(noticias, tema):
    """
    Filtra las noticias y las convierte en historias agrupadas.
    """

    relevantes, _ = filtrar_noticias(
        noticias,
        tema
    )

    grupos = agrupar_noticias(
        relevantes,
        tema=tema
    )

    for grupo in grupos:

        grupo["tendencia"] = calcular_tendencia(
            grupo
        )

        grupo["difusion"] = calcular_difusion(
            grupo
        )

    return grupos

def preparar_comparacion_internacional(
    noticias_internacionales,
    noticias_espana,
    tema,
    tema_internacional
):
    relevantes_internacionales, _ = filtrar_noticias(
        noticias_internacionales,
        tema_internacional
    )

    relevantes_espana, _ = filtrar_noticias(
        noticias_espana,
        tema
    )

    historias_internacionales = agrupar_noticias(
        relevantes_internacionales,
        tema=tema
    )

    conceptos_relacionados = detectar_conceptos_relacionados(
        historias_internacionales,
        tema=tema,
        tema_internacional=tema_internacional
    )

    historias_espana = agrupar_noticias(
        relevantes_espana,
        tema=tema
    )

    comparaciones = comparar_internacional_espana(
        historias_internacionales,
        historias_espana
    )

    return comparaciones, conceptos_relacionados

def mostrar_senales(grupos):
    """
    Muestra las historias detectadas de forma resumida.
    """

    if not grupos:

        st.info(
            "No se han detectado historias relevantes para este tema."
        )

        return

    total_publicaciones = sum(
        grupo["publicaciones"]
        for grupo in grupos
    )

    st.caption(
        f"{total_publicaciones} publicaciones relevantes · "
        f"{len(grupos)} historias detectadas"
    )

    for numero, grupo in enumerate(
        grupos[:MAX_SENALES],
        start=1
    ):

        st.markdown(
            f"**{numero:02d} · {grupo['tendencia']}**"
        )

        st.markdown(
            f"**{grupo['titulo']}**"
        )

        st.caption(
            f"{grupo['publicaciones']} publicaciones · "
            f"{grupo['fuentes']} fuentes"
        )

        st.write(
            f"{grupo['difusion']}"
        )

        with st.expander(
            "Ver publicaciones de esta historia"
        ):

            for noticia in grupo["noticias"]:

                titulo = noticia.get(
                    "title",
                    "Sin título"
                )

                url = noticia.get("url")

                fuente = noticia.get(
                    "domain",
                    "Fuente desconocida"
                )

                if url:

                    st.markdown(
                        f"- [{titulo}]({url}) "
                        f"— {fuente}"
                    )

                else:

                    st.write(
                        f"- {titulo} — {fuente}"
                    )


st.title("🌊 Radar de Olas")

st.caption(
    "Detecta señales de actividad internacional durante las últimas 24 horas."
)

with st.expander("📖 Cómo usar Radar de Olas"):

    st.markdown("""
    **1. Busca un tema**  
    Escribe algo que quieras vigilar: tecnología, IA, ciberseguridad, telecomunicaciones, geología…

    **2. El Radar busca actividad reciente**  
    Compara las noticias internacionales con las detectadas en España.

    **3. Las noticias se agrupan en historias**  
    El Radar intenta reunir publicaciones que hablan del mismo acontecimiento.

    **4. Observa las señales**  
    🔥 Aceleración · 📈 Movimiento · 📢 Amplificación · 🌱 Señal inicial

    **5. Mira las 🏄 alertas**  
    Son historias que pasan por el análisis de velocidad y pueden mostrar un avance entre la actividad internacional y España.

    **6. Explora las pistas relacionadas**  
    Los conceptos relacionados pueden ayudarte a descubrir nuevos términos y líneas de investigación.

    > **Radar de Olas no predice qué será viral. Detecta señales para que tú puedas investigar dónde empieza a formarse una ola.**
    """)

with st.expander("🌍 Lo que se mueve ahora", 
    expanded=False  
):
 
    opcion_tendencias = st.selectbox(
        "Mercado",
        [
            "🌍 Global",
            "🇪🇺 Europa",
            "🇺🇸 EE. UU.",
            "🇪🇸 España",
        ],
    )

    if opcion_tendencias == "🌍 Global":

        tendencias = obtener_tendencias_mundiales()

    elif opcion_tendencias == "🇪🇺 Europa":

        tendencias = []

        for geo in ["GB", "DE", "FR", "ES"]:

            for tendencia in obtener_tendencias_pais(geo):

                if tendencia not in tendencias:

                    tendencias.append(tendencia)

                if len(tendencias) >= 10:
                    break

            if len(tendencias) >= 10:
                break

    else:

        geos = {
            "🇺🇸 EE. UU.": "US",
            "🇪🇸 España": "ES",
        }

        tendencias = obtener_tendencias_pais(
            geos[opcion_tendencias]
        )

    if tendencias:

        for numero, tendencia in enumerate(
            tendencias[:10],
            start=1
        ):

            st.write(
                f"**{numero}.** {tendencia}"
            )

    else:

        st.caption(
            "No se han podido obtener tendencias en este momento."
        )

st.divider()


tema = st.text_input(
    "¿Qué quieres vigilar?",
    placeholder="Ej.: inteligencia artificial y empleo tecnológico"
)


ventana = 24


if st.button("🔎 Buscar", type="primary"):

    if not tema.strip():

        st.warning(
            "Introduce un tema para comenzar."
        )

    else:

        with st.spinner(
            "Buscando y analizando señales..."
        ):

            try:

                noticias_internacionales, tema_internacional = (
                    buscar_noticias_internacionales(
                        tema,
                        ventana
                    )
                )

                noticias_espana = buscar_noticias(
                    tema,
                    ventana
                )

                senales_internacionales = preparar_senales(
                    noticias_internacionales,
                    tema_internacional
                )

                senales_espana = preparar_senales(
                    noticias_espana,
                    tema
                )

                resultados_velocidad = analizar_velocidad(
                    noticias_internacionales,
                    tema_internacional
                )

                candidatas = seleccionar_candidatas(
                    resultados_velocidad
                )

                comparaciones, conceptos_relacionados = (
                    preparar_comparacion_internacional(
                        noticias_internacionales,
                        noticias_espana,
                        tema,
                        tema_internacional
                    )
                )

                if (
                    not senales_internacionales
                    and not senales_espana
                ):
                    st.info(
                        "No se han encontrado señales relevantes."
                    )

                st.subheader(
                    "💡 También relacionado con tu búsqueda"
                )

                if conceptos_relacionados:

                    st.caption(
                        "Términos que aparecen de forma recurrente "
                        "en distintas historias encontradas. "
                        "Pueden servir como nuevas pistas para explorar."
                    )

                    conceptos_mostrados = [
                        resultado["concepto"]
                        for resultado in conceptos_relacionados
                    ]

                    st.write(
                        " · ".join(conceptos_mostrados)
                    )

                else:

                    st.caption(
                        "No se han encontrado términos relacionados "
                        "con suficiente presencia en las historias."
                    )

                st.subheader(
                    "🌊 Alertas y Avance internacional / España"
                )

                if not candidatas:

                    st.info(
                        "No se han detectado alertas en este momento."
                    )

                else:

                    for candidata in candidatas:

                        historia_int = candidata["historia"]

                        with st.container(border=True):

                            st.markdown(
                                f"""
                                <div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">
                                    🏄 ALERTA · {candidatas.index(candidata) + 1:02d}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            f"### {historia_int['titulo']}"
                        )

                        st.write(
                            f"Actividad reciente: "
                            f"{candidata['publicaciones_recientes']} publicaciones · "
                            f"{candidata['fuentes_recientes']} fuentes"
                        )

                        st.write(
                            f"Última publicación hace "
                            f"{candidata['horas_desde_ultima']:.2f} h"
                        )

                        comparacion_candidata = next(
                            (
                                comparacion
                                for comparacion in comparaciones
                                if (
                                    comparacion["internacional"]["titulo"]
                                    == historia_int["titulo"]
                                )
                            ),
                            None
                        )

                        if comparacion_candidata is not None:

                            historia_es = (
                                comparacion_candidata["espana"]
                            )

                            brecha = (
                                calcular_brecha_internacional_espana(
                                    comparacion_candidata
                                )
                            )

                            if historia_es is not None:

                                st.caption(
                                    f"🇪🇸 Equivalente detectado: "
                                    f"{historia_es['titulo']}"
                                )

                                st.write(
                                    f"Internacional: "
                                    f"{historia_int['publicaciones']} publicaciones · "
                                    f"{historia_int['fuentes']} fuentes"
                                )

                                st.write(
                                    f"España: "
                                    f"{historia_es['publicaciones']} publicaciones · "
                                    f"{historia_es['fuentes']} fuentes"
                                )

                            else:

                                st.caption(
                                    "🇪🇸 Sin presencia detectada en España"
                                )

                                st.write(
                                    f"Internacional: "
                                    f"{historia_int['publicaciones']} publicaciones · "
                                    f"{historia_int['fuentes']} fuentes"
                                )

                                st.write(
                                    "España: 0 publicaciones · 0 fuentes"
                                )

                            st.write(
                                f"Avance internacional: "
                                f"+{brecha['brecha_publicaciones']} publicaciones · "
                                f"+{brecha['brecha_fuentes']} fuentes"
                            )

                            with st.expander(
                                "🔗 Ver publicaciones de esta historia",
                                expanded=False
                            ):

                                def mostrar_noticia(
                                    noticia,
                                    prefijo=""
                                ):

                                        titulo = noticia.get(
                                            "title",
                                            "Sin título"
                                        )

                                        url = noticia.get("url")

                                        fuente = noticia.get(
                                            "domain",
                                            "Fuente desconocida"
                                        )

                                        texto_copia = (
                                            f"Titular: {titulo}\n"
                                            f"Fuente: {fuente}\n"
                                            f"Enlace: {url or 'Sin enlace'}"
                                        )

                                        col_noticia, col_copiar = (
                                            st.columns([9, 1])
                                        )

                                        with col_noticia:

                                            if url:

                                                st.markdown(
                                                    f"{prefijo}[{titulo}]({url}) — {fuente}"
                                                )

                                            else:

                                                st.write(
                                                    f"{prefijo}{titulo} — {fuente}"
                                                )

                                        with col_copiar:

                                            import json

                                            texto_js = json.dumps(
                                                texto_copia,
                                                ensure_ascii=False
                                            )

                                            st.html(
                                                f"""
                                                <button
                                                    onclick="navigator.clipboard.writeText({texto_js})"
                                                    style="
                                                        width: 100%;
                                                        height: 32px;
                                                        border: 1px solid #ccc;
                                                        border-radius: 6px;
                                                        background: white;
                                                        cursor: pointer;
                                                        font-size: 16px;
                                                    "
                                                    title="Copiar noticia"
                                                >
                                                    📋
                                                </button>
                                                """,
                                                unsafe_allow_javascript=True,
                                            )

                                for noticia in historia_int["noticias"]:

                                    mostrar_noticia(noticia)

                                    if historia_es is not None:

                                        for noticia in historia_es["noticias"]:

                                            mostrar_noticia(
                                                noticia,
                                                prefijo="🇪🇸 "
                                            )

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader(
                        "🌍 Internacional"
                    )

                    mostrar_senales(
                        senales_internacionales
                    )

                with col2:

                    st.subheader(
                        "🇪🇸 España"
                    )

                    mostrar_senales(
                        senales_espana
                    )

            except Exception as e:

                st.error(
                    f"GDELT no está disponible: {e}"
                )
