from radar import buscar_noticias_internacionales
from filtro import filtrar_noticias
from agrupador import agrupar_noticias
from conceptos import detectar_conceptos_relacionados


tema = "OpenAI"

noticias, consulta = buscar_noticias_internacionales(
    tema,
    horas=24
)

relevantes, descartadas = filtrar_noticias(
    noticias,
    tema
)

historias = agrupar_noticias(
    relevantes,
    tema=tema
)

conceptos = detectar_conceptos_relacionados(
    historias,
    tema=tema
)

print()
print("=" * 60)
print("CONCEPTOS RELACIONADOS")
print("=" * 60)

print(
    f"Noticias relevantes: {len(relevantes)}"
)

print(
    f"Historias analizadas: {len(historias)}"
)

print()

for resultado in conceptos:
    print(
        f"- {resultado['concepto']} "
        f"({resultado['historias']} historias)"
    )