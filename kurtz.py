from laberinto import LaberintoLogico, LaberintoBayesiano

if __name__ == "__main__":
    opcion = input(
        "Introduce que laberinto quieres probar: B (bayesiano) o L (lógico) "
    )
    while opcion not in ["B", "b", "L", "l"]:
        opcion = input(
            "Introduce que laberinto quieres probar: B (bayesiano) o L (lógico)"
        )
    auto = input("Quieres que se ejecute de forma automática? ")
    while auto not in ["Si", "si", "Sí", "sí", "No", "no"]:
        auto = input("Quieres que se ejecute de forma automática? ")
    auto = auto in ["Si", "si", "Sí", "sí"]
    if opcion not in ["B", "b"]:
        LaberintoLogico(auto=auto)
    else:
        LaberintoBayesiano(auto=auto)
