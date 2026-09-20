from radar import (
    buscar_noticias,
    buscar_noticias_internacionales
)


tema = "inteligencia artificial"

print("=" * 80)
print("ESPAÑA")
print("=" * 80)

espana = buscar_noticias(
    tema,
    24
)

print("Noticias:", len(espana))

for noticia in espana[:10]:
    print(
        noticia["datetime"],
        "|",
        noticia["domain"],
        "|",
        noticia["title"]
    )


print()
print("=" * 80)
print("INTERNACIONAL / US")
print("=" * 80)

internacional = buscar_noticias_internacionales(
    tema,
    24
)

print("Noticias:", len(internacional))

for noticia in internacional[:10]:
    print(
        noticia["datetime"],
        "|",
        noticia["domain"],
        "|",
        noticia["title"]
    )