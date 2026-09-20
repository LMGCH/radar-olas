from collections import Counter
from radar import _buscar_google_news


CONFIGURACIONES = [
    ("ES", "es", "ES:es"),
    ("US", "en", "US:en"),
    ("DE", "de", "DE:de"),
    ("FR", "fr", "FR:fr"),
    ("JP", "ja", "JP:ja"),
]


for pais, idioma, ceid in CONFIGURACIONES:

    print()
    print("=" * 80)
    print(pais)
    print("=" * 80)

    noticias = _buscar_google_news(
        "artificial intelligence",
        24,
        idioma,
        pais,
        ceid
    )

    print("Noticias:", len(noticias))

    for noticia in noticias[:20]:

        print(
            noticia["datetime"],
            "|",
            noticia["domain"],
            "|",
            noticia["title"]
        )