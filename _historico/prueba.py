from filtro import es_relevante


noticia = {
    "title": "From France to Greece, wildfires rage across Europe's south"
}


resultado = es_relevante(
    noticia,
    "forest fires portugal"
)


print("¿Es relevante?", resultado)