from radar import buscar_noticias
from filtro import filtrar_noticias
from agrupador import titulo_sin_fuente


noticias = buscar_noticias(
    "artificial intelligence",
    24
)

relevantes, _ = filtrar_noticias(
    noticias,
    "artificial intelligence"
)

for noticia in relevantes[:10]:

    print()
    print("ANTES:")
    print(noticia["title"])

    print("DESPUÉS:")
    print(titulo_sin_fuente(noticia))

    print("FUENTE:")
    print(noticia["domain"])