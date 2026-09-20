from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import agrupar_noticias


tema = "artificial intelligence"


print("1. Buscando noticias...")

noticias = buscar_noticias(
    tema,
    24
)

print(
    "Noticias recibidas:",
    len(noticias)
)


print()
print("2. Filtrando...")

relevantes, descartadas = filtrar_noticias(
    noticias,
    tema
)

print(
    "Noticias relevantes:",
    len(relevantes)
)


print()
print("3. Agrupando...")

grupos = agrupar_noticias(
    relevantes
)

print(
    "Historias detectadas:",
    len(grupos)
)


print()
print("=" * 80)
print("HISTORIAS DETECTADAS")
print("=" * 80)


for numero, grupo in enumerate(
    grupos,
    start=1
):

    print()
    print(
        f"{numero}. {grupo['titulo']}"
    )

    print(
        f"   Publicaciones: "
        f"{grupo['publicaciones']}"
    )

    print(
        f"   Fuentes independientes: "
        f"{grupo['fuentes']}"
    )

    print(
        f"   Fuentes: "
        f"{', '.join(grupo['lista_fuentes'])}"
    )