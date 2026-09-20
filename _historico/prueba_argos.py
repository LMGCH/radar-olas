import argostranslate.translate as translate


PRUEBAS = [
    "humanoid",
    "manufacturing",
    "company",
    "acquires",
    "development",
    "talent",
    "robotics",
    "Unitree",
    "Meta",
    "robot",
]


print()
print("=" * 70)
print(" PRUEBA DIRECTA DE ARGOS TRANSLATE")
print("=" * 70)
print()


for texto in PRUEBAS:

    try:
        traduccion = translate.translate(
            texto,
            "en",
            "es"
        )

        print(
            f"{texto:20} -> {traduccion}"
        )

    except Exception as e:

        print(
            f"{texto:20} -> ERROR: {e}"
        )


print()
print("=" * 70)
print(" PRUEBA DE FRASES")
print("=" * 70)
print()


FRASES = [
    "humanoid robot",
    "robot manufacturing plant",
    "AI robotics company",
    "robotics industry",
    "humanoid robot development",
]


for frase in FRASES:

    try:
        traduccion = translate.translate(
            frase,
            "en",
            "es"
        )

        print()
        print(f"EN: {frase}")
        print(f"ES: {traduccion}")

    except Exception as e:

        print()
        print(f"EN: {frase}")
        print(f"ES: ERROR: {e}")


print()
print("=" * 70)
print(" FIN DE LA PRUEBA")
print("=" * 70)

