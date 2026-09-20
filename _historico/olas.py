from collections import Counter

from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias, palabras_clave
from datetime import datetime, timezone
from itertools import combinations
import re


def conceptos(noticia):
    """
    Obtiene los conceptos del titular
    eliminando únicamente el ruido estructural
    ya definido por el agrupador.
    """

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


# -------------------------------------------------
# RECOGIDA
# -------------------------------------------------

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


# -------------------------------------------------
# PESO DE CONCEPTOS
# -------------------------------------------------

frecuencia = Counter()

conceptos_historias = []

fuentes_por_concepto = {}

UMBRAL_PESO_RELACION = 0.25

for grupo in grupos:

    noticia = grupo["noticias"][0]

    palabras = conceptos(
        noticia
    )

    conceptos_historias.append(
        palabras
    )

    frecuencia.update(
        palabras
    )

    fuente = noticia.get(
        "domain",
        "Desconocida"
    )

    for palabra in palabras:

        if palabra not in fuentes_por_concepto:
            fuentes_por_concepto[palabra] = set()

        fuentes_por_concepto[palabra].add(
            fuente
        )

def peso(palabra):
    return 1 / frecuencia[palabra]

def diversidad_relacion(conceptos):
    return min(
        diversidad_fuentes(concepto)
        for concepto in conceptos
    )

def diversidad_fuentes(palabra):
    return len(
        fuentes_por_concepto.get(
            palabra,
            set()
        )
    )

def conceptos_distintivos(conceptos):
    return {
        palabra
        for palabra in conceptos
        if frecuencia[palabra] <= 4
    }


# -------------------------------------------------
# RELACIONES ENTRE HISTORIAS
# -------------------------------------------------

relaciones = []

for i in range(len(grupos)):

    for j in range(i + 1, len(grupos)):

        comunes = (
            conceptos_distintivos(
                conceptos_historias[i]
            )
            &
            conceptos_distintivos(
                conceptos_historias[j]
            )
        )

        diversidad_conceptos = {
            concepto: diversidad_fuentes(concepto)
            for concepto in comunes
        }

        if len(comunes) < 2:
            continue

        if max(
            peso(palabra)
            for palabra in comunes
        ) < UMBRAL_PESO_RELACION:
            continue

        fuerza = sum(
            peso(palabra)
            for palabra in comunes
        )

        diversidad = diversidad_relacion(
            comunes
        )

        relaciones.append(
            {
                "grupo_a": i,
                "grupo_b": j,
                "conceptos": sorted(comunes),
                "diversidad_conceptos": diversidad_conceptos,
                "fuerza": fuerza,
            }
        )


# -------------------------------------------------
# CONSTRUCCIÓN DE POSIBLES OLAS
# -------------------------------------------------

olas = []

for relacion in relaciones:

    grupo_a = grupos[
        relacion["grupo_a"]
    ]

    grupo_b = grupos[
        relacion["grupo_b"]
    ]

    ola_existente = None

    for ola in olas:

        if (
            grupo_a in ola["historias"]
            or grupo_b in ola["historias"]
        ):

            ola_existente = ola

            break

    if ola_existente:

        if grupo_a not in ola_existente["historias"]:

            ola_existente["historias"].append(
                grupo_a
            )

        if grupo_b not in ola_existente["historias"]:

            ola_existente["historias"].append(
                grupo_b
            )

        ola_existente["relaciones"].append(
            relacion
        )

        ola_existente["fuerza"] += (
            relacion["fuerza"]
        )

    else:

        olas.append(
            {
                "historias": [
                    grupo_a,
                    grupo_b,
                ],
                "relaciones": [
                    relacion
                ],
                "fuerza": relacion["fuerza"],
            }
        )


olas.sort(
    key=lambda ola: ola["fuerza"],
    reverse=True
)

# -------------------------------------------------
# PROSPECCIÓN DE RELACIONES DÉBILES
# -------------------------------------------------

relaciones_debiles = []

for i in range(len(grupos)):

    for j in range(i + 1, len(grupos)):

        comunes = (
            conceptos_historias[i]
            &
            conceptos_historias[j]
        )

        if len(comunes) < 2:
            continue

        conceptos_validos = {
            concepto: {
                "peso": peso(concepto),
                "fuentes": diversidad_fuentes(concepto),
            }
            for concepto in comunes
        }

        fuerza = sum(
            peso(concepto)
            for concepto in comunes
        )

        relaciones_debiles.append(
            {
                "grupo_a": i,
                "grupo_b": j,
                "conceptos": sorted(comunes),
                "fuerza": fuerza,
                "conceptos_validos": conceptos_validos,
            }
        )


relaciones_debiles.sort(
    key=lambda relacion: relacion["fuerza"],
    reverse=True
)


print()
print("=" * 80)
print("🔭 PROSPECCIÓN DE RELACIONES NO CONVERTIDAS EN RELACIÓN")
print("=" * 80)

for relacion in relaciones_debiles[:20]:

    if (
        relacion["grupo_a"],
        relacion["grupo_b"]
    ) in {
        (
            r["grupo_a"],
            r["grupo_b"]
        )
        for r in relaciones
    }:
        continue

    grupo_a = grupos[
        relacion["grupo_a"]
    ]

    grupo_b = grupos[
        relacion["grupo_b"]
    ]

    print()
    print(
        f"Fuerza potencial: "
        f"{relacion['fuerza']:.3f}"
    )

    print(
        f"Conceptos: "
        f"{', '.join(relacion['conceptos'])}"
    )

    print(
        f"A → "
        f"{grupo_a['titulo']}"
    )

    print(
        f"B → "
        f"{grupo_b['titulo']}"
    )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE REDES INDIRECTAS
# -------------------------------------------------

red = {}

for i in range(len(grupos)):
    red[i] = set()

for i in range(len(grupos)):

    for j in range(i + 1, len(grupos)):

        conceptos_a = conceptos_distintivos(
            conceptos_historias[i]
        )

        conceptos_b = conceptos_distintivos(
            conceptos_historias[j]
        )

        comunes = conceptos_a & conceptos_b

        if not comunes:
            continue

        red[i].add(j)
        red[j].add(i)


componentes = []
visitados = set()

for inicio in red:

    if inicio in visitados:
        continue

    componente = set()
    pendientes = [inicio]

    while pendientes:

        actual = pendientes.pop()

        if actual in visitados:
            continue

        visitados.add(actual)
        componente.add(actual)

        pendientes.extend(
            red[actual] - visitados
        )

    if len(componente) >= 3:
        componentes.append(
            sorted(componente)
        )


print()
print("=" * 80)
print("🕸️ PROSPECCIÓN DE REDES INDIRECTAS — CONCEPTOS DISTINTIVOS")
print("=" * 80)

print(
    f"Componentes encontrados: "
    f"{len(componentes)}"
)

for numero, componente in enumerate(
    componentes[:10],
    start=1
):

    print()
    print(
        f"RED {numero} — "
        f"{len(componente)} historias"
    )

    for indice in componente:

        grupo = grupos[indice]

        conceptos = sorted(
            conceptos_distintivos(
                conceptos_historias[indice]
            )
        )

        print(
            f"  [{indice}] "
            f"{grupo['titulo']}"
        )

        print(
            f"       Conceptos distintivos: "
            f"{', '.join(conceptos)}"
        )

        conexiones = []

    for otro in componente:

        if otro == indice:
            continue

        comunes = (
            conceptos_distintivos(
                conceptos_historias[indice]
            )
            &
            conceptos_distintivos(
                conceptos_historias[otro]
            )
        )

        if comunes:
            conexiones.append(
                (
                    otro,
                    sorted(comunes)
                )
            )

    for otro, comunes in conexiones:

        print(
            f"       ↳ conecta con [{otro}] "
            f"por: {', '.join(comunes)}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE CALIDAD DE CONEXIONES
# -------------------------------------------------

conexiones_prospectivas = []

for i in range(len(grupos)):

    for j in range(i + 1, len(grupos)):

        comunes = (
            conceptos_distintivos(
                conceptos_historias[i]
            )
            &
            conceptos_distintivos(
                conceptos_historias[j]
            )
        )

        if not comunes:
            continue

        detalles = []

        for concepto in sorted(comunes):

            detalles.append(
                {
                    "concepto": concepto,
                    "frecuencia": frecuencia[concepto],
                    "peso": peso(concepto),
                    "fuentes": diversidad_fuentes(concepto),
                }
            )

        fuerza = sum(
            detalle["peso"]
            for detalle in detalles
        )

        conexiones_prospectivas.append(
            {
                "grupo_a": i,
                "grupo_b": j,
                "detalles": detalles,
                "fuerza": fuerza,
            }
        )


conexiones_prospectivas.sort(
    key=lambda conexion: conexion["fuerza"],
    reverse=True
)


print()
print("=" * 80)
print("🔬 PROSPECCIÓN DE CALIDAD DE CONEXIONES")
print("=" * 80)

print(
    f"Conexiones encontradas: "
    f"{len(conexiones_prospectivas)}"
)

for numero, conexion in enumerate(
    conexiones_prospectivas[:20],
    start=1
):

    grupo_a = grupos[
        conexion["grupo_a"]
    ]

    grupo_b = grupos[
        conexion["grupo_b"]
    ]

    print()
    print(
        f"{numero}. Fuerza potencial: "
        f"{conexion['fuerza']:.3f}"
    )

    print(
        f"   A → {grupo_a['titulo']}"
    )

    print(
        f"   B → {grupo_b['titulo']}"
    )

    print(
        "   Conceptos compartidos:"
    )

    for detalle in conexion["detalles"]:

        print(
            f"      • {detalle['concepto']} "
            f"| frecuencia: {detalle['frecuencia']} "
            f"| peso: {detalle['peso']:.3f} "
            f"| fuentes: {detalle['fuentes']}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE CONTEXTO DE PARES DE CONCEPTOS
# -------------------------------------------------

pares_conceptos = {}

for i in range(len(grupos)):

    conceptos = sorted(
        conceptos_distintivos(
            conceptos_historias[i]
        )
    )

    for par in combinations(conceptos, 2):

        if par not in pares_conceptos:

            pares_conceptos[par] = {
                "historias": set(),
                "fuentes": set(),
            }

        pares_conceptos[par]["historias"].add(i)

        fuente = grupos[i]["noticias"][0].get(
            "domain",
            "Desconocida"
        )

        pares_conceptos[par]["fuentes"].add(
            fuente
        )


pares_relevantes = []

for par, datos in pares_conceptos.items():

    if len(datos["historias"]) < 2:
        continue

    fuerza = sum(
        peso(concepto)
        for concepto in par
    )

    pares_relevantes.append(
        {
            "par": par,
            "historias": datos["historias"],
            "fuentes": datos["fuentes"],
            "fuerza": fuerza,
        }
    )


pares_relevantes.sort(
    key=lambda par: (
        len(par["historias"]),
        len(par["fuentes"]),
        par["fuerza"],
    ),
    reverse=True
)


print()
print("=" * 80)
print("🧬 PROSPECCIÓN DE CONTEXTO DE PARES DE CONCEPTOS")
print("=" * 80)

print(
    f"Pares repetidos encontrados: "
    f"{len(pares_relevantes)}"
)


for numero, par in enumerate(
    pares_relevantes[:10],
    start=1
):

    print()
    print(
        f"{numero}. "
        f"{par['par'][0]} + {par['par'][1]}"
    )

    print(
        f"   Historias: "
        f"{len(par['historias'])}"
    )

    print(
        f"   Fuentes: "
        f"{len(par['fuentes'])}"
    )

    print(
        f"   Fuerza conceptual: "
        f"{par['fuerza']:.3f}"
    )

    for indice in sorted(par["historias"]):

        titulo = grupos[indice]["titulo"]

        palabras = palabras_clave(titulo)

        contexto = sorted(
            palabras
            - set(par["par"])
        )

        print()
        print(
            f"   → [{indice}] {titulo}"
        )

        print(
            f"      Contexto: "
            f"{', '.join(contexto)}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE CONTEXTO LOCAL
# -------------------------------------------------

print()
print("=" * 80)
print("🧪 PROSPECCIÓN DE CONTEXTO LOCAL")
print("=" * 80)


def contexto_concepto(titulo, concepto, ventana=3):

    palabras = palabras_clave(titulo)

    # Conservamos el orden original del titular.
    texto = titulo.lower()
    texto = re.sub(
        r"[^\wáéíóúüñ-]",
        " ",
        texto
    )

    palabras_originales = texto.split()

    concepto_normalizado = concepto.lower()

    posiciones = [
        indice
        for indice, palabra in enumerate(
            palabras_originales
        )
        if palabra == concepto_normalizado
    ]

    contextos = []

    for posicion in posiciones:

        inicio = max(
            0,
            posicion - ventana
        )

        final = min(
            len(palabras_originales),
            posicion + ventana + 1
        )

        contexto = palabras_originales[
            inicio:final
        ]

        contextos.append(
            contexto
        )

    return contextos


for numero, par in enumerate(
    pares_relevantes[:10],
    start=1
):

    concepto_a = par["par"][0]
    concepto_b = par["par"][1]

    print()
    print(
        f"{numero}. "
        f"{concepto_a} + {concepto_b}"
    )

    print(
        f"   Historias: "
        f"{len(par['historias'])}"
    )

    print(
        f"   Fuentes: "
        f"{len(par['fuentes'])}"
    )

    for indice in sorted(par["historias"]):

        titulo = grupos[indice]["titulo"]

        print()
        print(
            f"   → [{indice}] {titulo}"
        )

        contextos_a = contexto_concepto(
            titulo,
            concepto_a
        )

        contextos_b = contexto_concepto(
            titulo,
            concepto_b
        )

        print(
            f"      Contexto de "
            f"'{concepto_a}':"
        )

        for contexto in contextos_a:

            print(
                f"         {' '.join(contexto)}"
            )

        print(
            f"      Contexto de "
            f"'{concepto_b}':"
        )

        for contexto in contextos_b:

            print(
                f"         {' '.join(contexto)}"
            )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE RELACIONES VERBO–CONCEPTO
# -------------------------------------------------

VERBOS_COMUNES = {
    "es", "son", "está", "están",
    "ser", "estar", "tener", "tiene", "tienen",
    "hacer", "hace", "hacen",
    "haber", "hay",
    "poder", "puede", "pueden",
    "querer", "quiere", "quieren",
    "deber", "debe", "deben",
    "seguir", "sigue", "siguen",
    "estar", "llega", "llegará", "llegan",
    "anuncia", "anuncian", "anunciar",
    "lanza", "lanzan", "lanzar",
    "reduce", "reducen", "reducir",
    "aumenta", "aumentan", "aumentar",
    "mejora", "mejoran", "mejorar",
    "borra", "borrar",
    "elimina", "eliminar",
    "cuesta", "costar",
    "paga", "pagar",
    "impulsa", "impulsar",
    "transforma", "transformar",
    "marca", "marcar",
    "permite", "permitir",
    "incluye", "incluir",
    "presenta", "presentar",
    "reconoce", "reconocer",
    "culpa", "culpar",
    "pide", "pedir",
    "propone", "proponer",
    "alerta", "alertan",
    "alertar",
}


def palabras_titulo(titulo):

    texto = titulo.lower()

    texto = re.sub(
        r"[^\wáéíóúüñ-]",
        " ",
        texto
    )

    return texto.split()


relaciones_verbo_concepto = {}


for i in range(len(grupos)):

    titulo = grupos[i]["titulo"]

    palabras = palabras_titulo(titulo)

    conceptos = (
        conceptos_distintivos(
            conceptos_historias[i]
        )
        - VERBOS_COMUNES
    )

    for posicion, palabra in enumerate(palabras):

        if palabra not in VERBOS_COMUNES:
            continue

        inicio = max(
            0,
            posicion - 4
        )

        final = min(
            len(palabras),
            posicion + 5
        )

        contexto = palabras[
            inicio:final
        ]

        conceptos_cercanos = [
            concepto
            for concepto in conceptos
            if concepto in contexto
        ]

        for concepto in conceptos_cercanos:

            clave = (
                palabra,
                concepto
            )

            if clave not in relaciones_verbo_concepto:

                relaciones_verbo_concepto[clave] = {
                    "historias": set(),
                    "fuentes": set(),
                }

            relaciones_verbo_concepto[
                clave
            ]["historias"].add(i)

            fuente = grupos[i][
                "noticias"
            ][0].get(
                "domain",
                "Desconocida"
            )

            relaciones_verbo_concepto[
                clave
            ]["fuentes"].add(fuente)


relaciones_verbo_repetidas = []

for relacion, datos in relaciones_verbo_concepto.items():

    if len(datos["historias"]) < 2:
        continue

    verbo, concepto = relacion

    relaciones_verbo_repetidas.append(
        {
            "verbo": verbo,
            "concepto": concepto,
            "historias": datos["historias"],
            "fuentes": datos["fuentes"],
        }
    )


relaciones_verbo_repetidas.sort(
    key=lambda relacion: (
        len(relacion["historias"]),
        len(relacion["fuentes"]),
    ),
    reverse=True
)


print()
print("=" * 80)
print("🔗 PROSPECCIÓN DE RELACIONES VERBO–CONCEPTO")
print("=" * 80)

print(
    f"Relaciones repetidas encontradas: "
    f"{len(relaciones_verbo_repetidas)}"
)


for numero, relacion in enumerate(
    relaciones_verbo_repetidas[:20],
    start=1
):

    print()
    print(
        f"{numero}. "
        f"{relacion['verbo']} → "
        f"{relacion['concepto']}"
    )

    print(
        f"   Historias: "
        f"{len(relacion['historias'])}"
    )

    print(
        f"   Fuentes: "
        f"{len(relacion['fuentes'])}"
    )

    for indice in sorted(
        relacion["historias"]
    ):

        print(
            f"   → [{indice}] "
            f"{grupos[indice]['titulo']}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE PERFILES CONCEPTUALES
# -------------------------------------------------

print()
print("=" * 80)
print("🧩 PROSPECCIÓN DE PERFILES CONCEPTUALES")
print("=" * 80)


perfiles_historias = []

for i in range(len(grupos)):

    perfil = conceptos_distintivos(
        conceptos_historias[i]
    )

    perfiles_historias.append(
        perfil
    )


comparaciones_perfiles = []

for i in range(len(perfiles_historias)):

    for j in range(i + 1, len(perfiles_historias)):

        comunes = (
            perfiles_historias[i]
            &
            perfiles_historias[j]
        )

        if not comunes:
            continue

        union = (
            perfiles_historias[i]
            |
            perfiles_historias[j]
        )

        similitud_perfil = (
            len(comunes)
            /
            len(union)
        )

        fuentes = {
            grupos[i]["noticias"][0].get(
                "domain",
                "Desconocida"
            ),
            grupos[j]["noticias"][0].get(
                "domain",
                "Desconocida"
            ),
        }

        comparaciones_perfiles.append(
            {
                "grupo_a": i,
                "grupo_b": j,
                "comunes": comunes,
                "similitud": similitud_perfil,
                "fuentes": fuentes,
            }
        )


comparaciones_perfiles.sort(
    key=lambda comparacion: (
        len(comparacion["comunes"]),
        comparacion["similitud"],
        len(comparacion["fuentes"]),
    ),
    reverse=True
)


print(
    f"Comparaciones con conceptos compartidos: "
    f"{len(comparaciones_perfiles)}"
)


for numero, comparacion in enumerate(
    comparaciones_perfiles[:20],
    start=1
):

    grupo_a = grupos[
        comparacion["grupo_a"]
    ]

    grupo_b = grupos[
        comparacion["grupo_b"]
    ]

    print()
    print(
        f"{numero}. "
        f"Conceptos comunes: "
        f"{len(comparacion['comunes'])}"
    )

    print(
        f"   Similitud de perfil: "
        f"{comparacion['similitud']:.3f}"
    )

    print(
        f"   Fuentes: "
        f"{len(comparacion['fuentes'])}"
    )

    print(
        f"   Conceptos: "
        f"{', '.join(sorted(comparacion['comunes']))}"
    )

    print(
        f"   A → "
        f"{grupo_a['titulo']}"
    )

    print(
        f"   B → "
        f"{grupo_b['titulo']}"
    )

    print("-" * 80)


# -------------------------------------------------
# PROSPECCIÓN DE NÚCLEOS CONCEPTUALES
# -------------------------------------------------

pares_conceptos = {}

for i in range(len(perfiles_historias)):

    conceptos = sorted(
        perfiles_historias[i]
    )

    for a, concepto_a in enumerate(conceptos):

        for concepto_b in conceptos[a + 1:]:

            par = (
                concepto_a,
                concepto_b
            )

            if par not in pares_conceptos:

                pares_conceptos[par] = {
                    "historias": set(),
                    "fuentes": set(),
                    "conceptos_contexto": set(),
                }

            datos = pares_conceptos[par]

            datos["historias"].add(i)

            fuente = grupos[i]["noticias"][0].get(
                "domain",
                "Desconocida"
            )

            datos["fuentes"].add(
                fuente
            )

            datos["conceptos_contexto"].update(
                perfiles_historias[i]
            )


# -------------------------------------------------
# SELECCIÓN DE NÚCLEOS
# -------------------------------------------------

nucleos = []

for par, datos in pares_conceptos.items():

    if len(datos["historias"]) < 2:
        continue

    nucleos.append(
        {
            "par": par,
            "historias": datos["historias"],
            "fuentes": datos["fuentes"],
            "contexto": datos["conceptos_contexto"],
        }
    )


nucleos.sort(
    key=lambda nucleo: (
        len(nucleo["historias"]),
        len(nucleo["fuentes"]),
    ),
    reverse=True
)

# -------------------------------------------------
# PROSPECCIÓN DE CONTEXTO DE NÚCLEOS
# -------------------------------------------------

print()
print("=" * 80)
print("🔬 PROSPECCIÓN DE CONTEXTO DE NÚCLEOS")
print("=" * 80)

for numero, nucleo in enumerate(
    nucleos[:10],
    start=1
):

    conceptos_nucleo = set(
        nucleo["par"]
    )

    historias = nucleo["historias"]

    contexto = {}

    for indice in historias:

        perfil = perfiles_historias[indice]

        fuente = grupos[indice]["noticias"][0].get(
            "domain",
            "Desconocida"
        )

        for concepto in perfil:

            if concepto in conceptos_nucleo:
                continue

            if concepto not in contexto:

                contexto[concepto] = {
                    "historias": set(),
                    "fuentes": set(),
                }

            contexto[concepto]["historias"].add(
                indice
            )

            contexto[concepto]["fuentes"].add(
                fuente
            )

    contexto_ordenado = sorted(
        contexto.items(),
        key=lambda item: (
            len(item[1]["historias"]),
            len(item[1]["fuentes"]),
        ),
        reverse=True
    )

    print()

    print(
        f"{numero}. "
        f"Núcleo: "
        f"{nucleo['par'][0]} + "
        f"{nucleo['par'][1]}"
    )

    print(
        f"   Historias: "
        f"{len(historias)}"
    )

    print(
        f"   Fuentes independientes: "
        f"{len(nucleo['fuentes'])}"
    )

    print(
        "   Conceptos asociados:"
    )

    for concepto, datos in contexto_ordenado[:15]:

        print(
            f"      • {concepto} "
            f"| historias: "
            f"{len(datos['historias'])} "
            f"| fuentes: "
            f"{len(datos['fuentes'])}"
        )

    print()

    print(
        "   Historias que forman el núcleo:"
    )

    for indice in sorted(historias):

        print(
            f"      → [{indice}] "
            f"{grupos[indice]['titulo']}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE NÚCLEOS CONECTADOS
# -------------------------------------------------

print()
print("=" * 80)
print("🕸️ PROSPECCIÓN DE NÚCLEOS CONECTADOS")
print("=" * 80)


# Dos núcleos están conectados cuando
# comparten al menos una historia.

conexiones_nucleos = []

for i in range(len(nucleos)):

    for j in range(i + 1, len(nucleos)):

        nucleo_a = nucleos[i]
        nucleo_b = nucleos[j]

        historias_comunes = (
            nucleo_a["historias"]
            &
            nucleo_b["historias"]
        )

        if not historias_comunes:
            continue

        conexiones_nucleos.append(
            {
                "nucleo_a": i,
                "nucleo_b": j,
                "historias_comunes": historias_comunes,
            }
        )


print(
    f"Conexiones entre núcleos: "
    f"{len(conexiones_nucleos)}"
)


for numero, conexion in enumerate(
    conexiones_nucleos,
    start=1
):

    nucleo_a = nucleos[
        conexion["nucleo_a"]
    ]

    nucleo_b = nucleos[
        conexion["nucleo_b"]
    ]

    print()

    print(
        f"{numero}. "
        f"{nucleo_a['par'][0]} + "
        f"{nucleo_a['par'][1]}"
    )

    print(
        "   ↕"
    )

    print(
        f"   {nucleo_b['par'][0]} + "
        f"{nucleo_b['par'][1]}"
    )

    print(
        f"   Historias puente: "
        f"{len(conexion['historias_comunes'])}"
    )

    for indice in sorted(
        conexion["historias_comunes"]
    ):

        print(
            f"      → [{indice}] "
            f"{grupos[indice]['titulo']}"
        )

    print("-" * 80)

# -------------------------------------------------
# PROSPECCIÓN DE DENSIDAD DE CONEXIONES ENTRE NÚCLEOS
# -------------------------------------------------

print()
print("=" * 80)
print("📐 PROSPECCIÓN DE DENSIDAD DE CONEXIONES ENTRE NÚCLEOS")
print("=" * 80)


for numero, conexion in enumerate(
    conexiones_nucleos,
    start=1
):

    nucleo_a = nucleos[
        conexion["nucleo_a"]
    ]

    nucleo_b = nucleos[
        conexion["nucleo_b"]
    ]

    historias_puente = (
        conexion["historias_comunes"]
    )

    fuentes_puente = set()

    for indice in historias_puente:

        fuente = grupos[indice]["noticias"][0].get(
            "domain",
            "Desconocida"
        )

        fuentes_puente.add(
            fuente
        )

    historias_a = nucleo_a["historias"]
    historias_b = nucleo_b["historias"]

    union_historias = (
        historias_a
        |
        historias_b
    )

    densidad = (
        len(historias_puente)
        /
        len(union_historias)
        if union_historias
        else 0
    )

    print()

    print(
        f"{numero}. "
        f"{nucleo_a['par'][0]} + "
        f"{nucleo_a['par'][1]}"
    )

    print(
        "   ↕"
    )

    print(
        f"   {nucleo_b['par'][0]} + "
        f"{nucleo_b['par'][1]}"
    )

    print(
        f"   Historias del núcleo A: "
        f"{len(historias_a)}"
    )

    print(
        f"   Historias del núcleo B: "
        f"{len(historias_b)}"
    )

    print(
        f"   Historias puente: "
        f"{len(historias_puente)}"
    )

    print(
        f"   Fuentes de las historias puente: "
        f"{len(fuentes_puente)}"
    )

    print(
        f"   Historias únicas en ambos núcleos: "
        f"{len(union_historias)}"
    )

    print(
        f"   Densidad de conexión: "
        f"{densidad:.3f}"
    )

    print("-" * 80)

# -------------------------------------------------
# CONSTRUCCIÓN DE POSIBLES OLAS
# -------------------------------------------------

olas = []

for relacion in relaciones:

    grupo_a = grupos[
        relacion["grupo_a"]
    ]

    grupo_b = grupos[
        relacion["grupo_b"]
    ]

    ola_existente = None

    for ola in olas:

        if (
            grupo_a in ola["historias"]
            or grupo_b in ola["historias"]
        ):

            ola_existente = ola

            break

    if ola_existente:

        if grupo_a not in ola_existente["historias"]:

            ola_existente["historias"].append(
                grupo_a
            )

        if grupo_b not in ola_existente["historias"]:

            ola_existente["historias"].append(
                grupo_b
            )

        ola_existente["relaciones"].append(
            relacion
        )

        ola_existente["fuerza"] += (
            relacion["fuerza"]
        )

    else:

        olas.append(
            {
                "historias": [
                    grupo_a,
                    grupo_b,
                ],
                "relaciones": [
                    relacion
                ],
                "fuerza": relacion["fuerza"],
            }
        )


olas.sort(
    key=lambda ola: ola["fuerza"],
    reverse=True
)
# -------------------------------------------------
# DIAGNÓSTICO DE POSIBLES OLAS
# -------------------------------------------------

print()
print("=" * 80)
print("🌊 DIAGNÓSTICO DE POSIBLES OLAS")
print("=" * 80)

print(
    f"Olas candidatas: {len(olas)}"
)

print()

for numero, ola in enumerate(
    olas[:10],
    start=1
):

    print(
        f"{numero:>2}. "
        f"Fuerza: {ola['fuerza']:.3f} | "
        f"Historias: {len(ola['historias'])} | "
        f"Relaciones: {len(ola['relaciones'])}"
    )

    fuentes_ola = {
        noticia.get("domain", "Desconocida")
        for historia in ola["historias"]
        for noticia in historia["noticias"]
    }

    publicaciones_ola = sum(
        len(historia["noticias"])
        for historia in ola["historias"]
    )

    ahora = datetime.now(timezone.utc)

    periodos = {
        "0-2 h": {
            "publicaciones": 0,
            "fuentes": set(),
        },
        "2-4 h": {
            "publicaciones": 0,
            "fuentes": set(),
        },
        "4-8 h": {
            "publicaciones": 0,
            "fuentes": set(),
        },
        "8-16 h": {
            "publicaciones": 0,
            "fuentes": set(),
        },
        "16-24 h": {
            "publicaciones": 0,
            "fuentes": set(),
        },
    }

    for historia in ola["historias"]:

        for noticia in historia["noticias"]:

            fecha = noticia.get("datetime")

            if not fecha:
                continue

            horas = (
                ahora - fecha
            ).total_seconds() / 3600

            if horas <= 2:
                periodo = "0-2 h"

            elif horas <= 4:
                periodo = "2-4 h"

            elif horas <= 8:
                periodo = "4-8 h"

            elif horas <= 16:
                periodo = "8-16 h"

            elif horas <= 24:
                periodo = "16-24 h"

            else:
                continue

            periodos[periodo]["publicaciones"] += 1

            periodos[periodo]["fuentes"].add(
                noticia.get(
                    "domain",
                    "Desconocida"
                )
            )

    print(
        f"    Fuentes distintas: "
        f"{len(fuentes_ola)}"
    )

    print(
        f"    Publicaciones totales: "
        f"{publicaciones_ola}"
    )

    print(
        "    Actividad temporal:"
    )

    for periodo, datos in periodos.items():

        print(
            f"      {periodo:<7} → "
            f"{datos['publicaciones']} publicaciones | "
            f"{len(datos['fuentes'])} fuentes"
        )

    # -------------------------------------------------
    # DIVERSIDAD TEMPORAL DE FUENTES
    # -------------------------------------------------

    fuentes_temporales = [
        len(periodos["16-24 h"]["fuentes"]),
        len(periodos["8-16 h"]["fuentes"]),
        len(periodos["4-8 h"]["fuentes"]),
        len(periodos["2-4 h"]["fuentes"]),
        len(periodos["0-2 h"]["fuentes"]),
    ]

    print(
        f"    Diversidad temporal de fuentes: "
        f"{fuentes_temporales}"
    )

    # -------------------------------------------------
    # NUEVAS FUENTES POR PERIODO
    # -------------------------------------------------

    nuevas_fuentes = []

    fuentes_acumuladas = set()

    for periodo in [
        "16-24 h",
        "8-16 h",
        "4-8 h",
        "2-4 h",
        "0-2 h",
    ]:

        fuentes_periodo = periodos[periodo]["fuentes"]

        nuevas = fuentes_periodo - fuentes_acumuladas

        nuevas_fuentes.append(
            len(nuevas)
        )

        fuentes_acumuladas.update(
            fuentes_periodo
        )

    print(
        f"    Nuevas fuentes por periodo: "
        f"{nuevas_fuentes}"
    )

    # -------------------------------------------------
    # CONTINUIDAD DE RENOVACIÓN DE FUENTES
    # -------------------------------------------------

    continuidad_actual = 0

    for nuevas in reversed(nuevas_fuentes):
        if nuevas > 0:
            continuidad_actual += 1
        else:
            break

    print(
        f"    Continuidad reciente de nuevas fuentes: "
        f"{continuidad_actual} periodos"
    )

    # -------------------------------------------------
    # MAYOR RACHA DE RENOVACIÓN DE FUENTES
    # -------------------------------------------------

    racha_actual = 0
    racha_maxima = 0

    for nuevas in nuevas_fuentes:

        if nuevas > 0:
            racha_actual += 1
            racha_maxima = max(
                racha_maxima,
                racha_actual
            )
        else:
            racha_actual = 0

    print(
        f"    Mayor racha de nuevas fuentes: "
        f"{racha_maxima} periodos"
    )

    # -------------------------------------------------
    # PENDIENTES TEMPORALES
    # -------------------------------------------------

    actividad = [
        periodos["16-24 h"]["publicaciones"],
        periodos["8-16 h"]["publicaciones"],
        periodos["4-8 h"]["publicaciones"],
        periodos["2-4 h"]["publicaciones"],
        periodos["0-2 h"]["publicaciones"],
    ]

    # -------------------------------------------------
    # EDAD MEDIA DE LA ACTIVIDAD
    # -------------------------------------------------

    edades = []

    for grupo in ola["historias"]:

        for noticia in grupo["noticias"]:

            fecha = noticia.get("datetime")

            if fecha is not None:

                edad_horas = (
                    ahora - fecha
                ).total_seconds() / 3600

                edades.append(
                    max(0, edad_horas)
                )

    if edades:

        edad_media = sum(edades) / len(edades)

        print(
            f"    Edad media de la actividad: "
            f"{edad_media:.2f} horas"
        )

    else:

        print(
            "    Edad media de la actividad: "
            "sin datos"
        )

    # -------------------------------------------------
    # POSICIÓN TEMPORAL DE LA ACTIVIDAD
    # -------------------------------------------------

    total_actividad = sum(actividad)

    if total_actividad > 0:

        posicion_actividad = sum(
            indice * publicaciones
            for indice, publicaciones
            in enumerate(actividad)
        ) / total_actividad

        print(
            f"    Posición temporal de la actividad: "
            f"{posicion_actividad:.2f} / 4"
        )

    else:

        print(
            "    Posición temporal de la actividad: "
            "sin actividad"
        )

    # Evolución desde la parte antigua de la ventana
    # hasta el centro de la actividad.
    pendiente_temprana = (
        actividad[2] - actividad[0]
    ) / 2

    # Evolución desde el centro de la actividad
    # hasta las publicaciones más recientes.
    pendiente_reciente = (
        actividad[4] - actividad[2]
    ) / 2

    print(
        f"    Pendiente temprana: "
        f"{pendiente_temprana:+.2f}"
    )

    print(
        f"    Pendiente reciente: "
        f"{pendiente_reciente:+.2f}"
    )

    # -------------------------------------------------
    # ACTIVIDAD RECIENTE
    # -------------------------------------------------

    actividad_reciente = (
        actividad[3]
        + actividad[4]
    )

    if total_actividad > 0:

        proporcion_reciente = (
            actividad_reciente
            / total_actividad
        )

        print(
            f"    Actividad últimas 4 h: "
            f"{proporcion_reciente:.2%}"
        )

    else:

        print(
            "    Actividad reciente: "
            "sin actividad"
        )

    # -------------------------------------------------
    # RENOVACIÓN RECIENTE DE FUENTES
    # -------------------------------------------------

    fuentes_recientes = (
        periodos["2-4 h"]["fuentes"]
        | periodos["0-2 h"]["fuentes"]
    )

    fuentes_anteriores = (
        periodos["4-8 h"]["fuentes"]
        | periodos["8-16 h"]["fuentes"]
        | periodos["16-24 h"]["fuentes"]
    )

    nuevas_fuentes_recientes = (
        fuentes_recientes - fuentes_anteriores
    )

    print(
        f"    Nuevas fuentes últimas 4 h: "
        f"{len(nuevas_fuentes_recientes)}"
    )


    # -------------------------------------------------
    # ACELERACIÓN TEMPORAL
    # -------------------------------------------------

    aceleracion = (
        pendiente_reciente - pendiente_temprana
    )

    print(
        f"    Aceleración temporal: "
        f"{aceleracion:+.2f}"
    )

    print(
        "    Historias:"
    )

    for historia in ola["historias"]:

        print(
            f"      → {historia['titulo']}"
        )

    print(
        "    Relaciones:"
    )

    for relacion in ola["relaciones"]:

        print(
            f"      • "
            f"{', '.join(relacion['conceptos'])}"
        )

    print("-" * 80)