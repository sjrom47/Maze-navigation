import random
from agentes import AgenteLogico, AgenteBayesiano
from algoritmos_busqueda import BusquedaLogica, BusquedaBayesiana
import time

"""
Trabajo final fundamentos inteligencia artificial Sergio Jimenez Romero
"""


class BaseLaberinto:
    """
    Clase con funciones comunes a ambos laberintos
    """

    def __init__(self, n, sol) -> None:
        """
        Constructor de la clase

        Args:
            n (int): tamaño del laberinto
            sol (bool): si se quiere mostrar el laberinto solucionado
        """
        self.sol = sol
        self.tamaño = n
        self.caracteres_Wilson = "CW  "
        self.kurt_encontrado = False
        self.casillas_seguras = []

        self.pos = [0, 0]
        self.visitados = [self.pos.copy()]
        self.vistas = [self.pos.copy()]
        self.en_salida = False
        self.en_monstruo = False
        self.monstruo_muerto = False

        self.grito = False

    def __str__(self) -> str:
        """
        Representación del laberinto

        Returns:
            str: la representación del estado del laberinto
        """
        resultado = ""
        for x, fila in enumerate(self.estado):
            resultado += "-----" * self.tamaño + "\n"
            for i, j in zip(range(0, 3, 2), range(1, 4, 2)):
                for y, celda in enumerate(fila):
                    resultado += (
                        f"|{celda[i]} {celda[j]}|"
                        if [x, y] in self.visitados or self.sol or [x, y] in self.vistas
                        else "|? ?|"
                    )
                resultado += "\n"
        resultado += "-----" * self.tamaño + "\n"
        for i in self.adyacentes:
            resultado += self.mensajes[i] + " "
        if self.grito:
            resultado = resultado.replace("Hueles algo", self.mensajes[5])
        return resultado

    def pedir_accion(self):
        """
        Pide una acción al jugador

        Returns:
            str: la accion elegida
        """
        inp = input("Introduce una acción: ")
        accion = self.input_a_acciones.get(inp.upper(), None)
        while not accion:
            print("Se ha Introducido una accion no válida")
            inp = input("Introduce una acción: ")
            accion = self.input_a_acciones.get(inp.upper(), None)
        return accion


class LaberintoLogico(BaseLaberinto):
    """
    Clase que crea y gestiona el laberinto lógico
    """

    def __init__(self, n=6, sol=False, auto=False) -> None:
        """
        Constructor del laberinto lógico

        Args:
            n (int, optional): tamaño del laberinto. Defaults to 6.
            sol (bool, optional): si se muestra solucionado o no. Defaults to False.
            auto (bool, optional): si debe ejecutarse el algoritmo de búsqueda. Defaults to False.
        """
        super().__init__(n, sol)
        self.busqueda = None
        if auto:
            self.busqueda = BusquedaLogica(n)

        self.estado = self.generar_estado_inicial()

        self.granada = True

        self.traduccion_a_perceptos = {"P   ": 0, "M   ": 1, "S   ": 2}
        self.mensajes = {
            0: "Hay una brisa",
            1: "Hueles algo",
            2: "Ves una luz",
            5: "Oyes un grito",
        }
        self.input_a_acciones = {
            "W": "UP",
            "S": "DOWN",
            "A": "LEFT",
            "D": "RIGHT",
            "G": "GRENADE",
            "E": "EXIT",
        }
        self.agente = AgenteLogico(n)
        self.jugando = True
        self.percepto = self.generar_percepto()

        self.ejecutar_laberinto()

    def generar_estado_inicial(self):
        """
        Genera el estado inicial del laberinto

        Returns:
            list: matriz que representa el laberinto
        """
        base = [["    " for _ in range(self.tamaño)] for _ in range(self.tamaño)]
        base[0][0] = self.caracteres_Wilson
        for i in ["P   ", "P   ", "P   ", "M   ", "CK  ", "S   "]:
            x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            while base[x][y] != "    ":
                x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            base[x][y] = i
        return base

    def generar_percepto(self):
        """
        Genera un percepto en base a la posición del jugador. Ese percepto es procesado
        por el agente lógico, que devuelve sus predicciones. Estas se verifican y se guardan
        según su tipo

        Returns:
            list: lista con información de los perceptos (orden de las diapositivas mas kurtz al final)
        """
        base = [0 for _ in range(9)]
        if self.pos[1] == 0:
            base[5] = 1
        elif self.pos[1] == self.tamaño - 1:
            base[6] = 1
        if self.pos[0] == 0:
            base[3] = 1
        elif self.pos[0] == self.tamaño - 1:
            base[4] = 1
        if self.grito:
            base[7] = 1
        if self.kurt_encontrado:
            base[8] = 1
        self.adyacentes = self.comprobar_adyacentes()
        for i in self.adyacentes:
            base[i] = 1
        casillas_seguras, monstruo, precipicios, salida = self.agente.process_percept(
            base, self.pos, self.visitados, self.en_salida, self.en_monstruo
        )
        conocidas = [casillas_seguras, monstruo, precipicios, salida]
        self.comprobar_predicciones(conocidas)
        self.casillas_seguras.extend(casillas_seguras + salida)
        self.vistas.extend(casillas_seguras + monstruo + precipicios + salida)
        return base

    def comprobar_adyacentes(self):
        """
        Comprueba el contenido de las casillas adyacentes a la actual

        Returns:
            list: los contenidos de esas casillas
        """
        ady = []
        if self.pos[1] > 0:
            izq = self.traduccion_a_perceptos.get(
                self.estado[self.pos[0]][self.pos[1] - 1], None
            )
        else:
            izq = None
        if self.pos[1] < self.tamaño - 1:
            der = self.traduccion_a_perceptos.get(
                self.estado[self.pos[0]][self.pos[1] + 1], None
            )
        else:
            der = None

        if self.pos[0] > 0:
            up = self.traduccion_a_perceptos.get(
                self.estado[self.pos[0] - 1][self.pos[1]], None
            )
        else:
            up = None
        if self.pos[0] < self.tamaño - 1:
            down = self.traduccion_a_perceptos.get(
                self.estado[self.pos[0] + 1][self.pos[1]], None
            )
        else:
            down = None
        for i in [izq, der, up, down]:
            if i is not None:
                ady.append(i)
        return ady

    def comprobar_predicciones(self, predicciones):
        """
        Verificación de las predicciones del modelo lógico

        Args:
            predicciones (list): lista con listas para cada tipo de predicción
        """
        if self.jugando:
            dict_pred = {0: "    ", 1: "M   ", 2: "P   ", 3: "S   "}
            try:
                for ind, clase in enumerate(predicciones):
                    for prediccion in clase:
                        simbolo = dict_pred[ind]
                        if self.estado[prediccion[0]][prediccion[1]] != "CK  ":
                            assert simbolo == self.estado[prediccion[0]][prediccion[1]]
            except AssertionError as e:
                print("El modelo lógico ha hecho una predicción errónea")

    def ejecutar_accion(self, accion):
        """
        Dada una acción la ejecuta

        Args:
            accion (str): la accion
        """
        pos_antes = self.pos.copy()
        if accion == "LEFT":
            if self.percepto[5] != 1:
                self.pos[1] -= 1
            else:
                print("No te puedes mover hacia la izquierda, hay una pared")
        elif accion == "RIGHT":
            if self.percepto[6] != 1:
                self.pos[1] += 1
            else:
                print("No te puedes mover hacia la derecha, hay una pared")
        elif accion == "UP":
            if self.percepto[3] != 1:
                self.pos[0] -= 1
            else:
                print("No te puedes mover hacia arriba, hay una pared")
        elif accion == "DOWN":
            if self.percepto[4] != 1:
                self.pos[0] += 1
            else:
                print("No te puedes mover hacia abajo, hay una pared")
        elif accion == "GRENADE":
            if self.granada:
                self.granada = False
                if self.percepto[1] == 1:
                    self.grito = True
                    self.monstruo_muerto = True

            else:
                print("No te quedan granadas")

        elif accion == "EXIT":
            if self.en_salida:
                if self.kurt_encontrado:
                    print("Enhorabuena, has escapado del laberinto")
                else:
                    print("Escapas del laberinto, pero dejas a Kurt abandonado")
                self.jugando = False
            else:
                print("No estás en la salida")
        if pos_antes != self.pos:
            if self.en_salida:
                self.estado[pos_antes[0]][pos_antes[1]] = "S   "
                self.en_salida = False
            elif self.en_monstruo:
                self.estado[pos_antes[0]][pos_antes[1]] = "M   "
                self.en_monstruo = False
            else:
                self.estado[pos_antes[0]][pos_antes[1]] = "    "
            self.comprobaciones_tras_mover()
            self.estado[self.pos[0]][self.pos[1]] = self.caracteres_Wilson

    def comprobaciones_tras_mover(self):
        """
        Comprueba que debe ocurrir tras el movimiento del jugador
        """
        contenido_casilla = self.traduccion_a_perceptos.get(
            self.estado[self.pos[0]][self.pos[1]], None
        )
        if contenido_casilla in [0, 1]:
            if not self.monstruo_muerto:
                self.jugando = False
            if contenido_casilla == 0:
                print("Te has caído por un precipicio. Misión fallida")
            elif not self.monstruo_muerto:
                print("El monstruo te ha comido. Misión fallida")
            else:
                self.en_monstruo = True
                print("Ves el cadaver del monstruo")
        elif contenido_casilla == 2:
            self.en_salida = True
            if self.busqueda:
                self.busqueda.pos_salida = self.pos.copy()
            print("Estas en la salida")
        elif self.estado[self.pos[0]][self.pos[1]] == "CK  ":
            self.kurt_encontrado = True
            if self.busqueda:
                self.busqueda.kurt_encontrado = True
            self.caracteres_Wilson = "CWCK"

        if self.pos not in self.visitados:
            self.visitados.append(self.pos.copy())
        self.percepto = self.generar_percepto()

    def ejecutar_laberinto(self):
        """
        Ejecuta el laberinto
        """
        print("Bienvenido al laberinto")
        print(
            "Las acciones disponibles son: W (up), S (down), A (left), D (right), E (exit) y G (grenade)"
        )
        while self.jugando:
            print(str(self))

            if not self.busqueda:
                accion = self.pedir_accion()
            else:
                accion = self.busqueda.give_next_move(
                    self.casillas_seguras, self.pos, self.visitados
                )
            self.ejecutar_accion(accion)


class LaberintoBayesiano(BaseLaberinto):
    """
    Clase que ejecuta el laberinto Bayesiano
    """

    def __init__(self, n=6, sol=False, auto=False) -> None:
        """
        Constructor de la clase

        Args:
            n (int, optional): tamaño del laberinto. Defaults to 6.
            sol (bool, optional): si se debe mostrar solucionado. Defaults to False.
            auto (bool, optional): si se debe emplear el algoritmo de búsqueda. Defaults to False.
        """
        super().__init__(n, sol)
        self.estado = self.generar_estado_inicial()
        self.busqueda = None
        if auto:
            self.busqueda = BusquedaBayesiana(n)
        self.dardo = True
        self.frontera = [(0, 1), (1, 0)]
        self.agente = AgenteBayesiano(n)

        self.traduccion_a_perceptos = {"F": 0, "P": 1, "D": 2, "M": 3, "S": 4}
        self.mensajes = {
            0: "Huele a queroseno",
            1: "El suelo cruje",
            2: "Ves cables",
            3: "Hueles algo",
            4: "Ves una luz",
            5: "Oyes un grito",
        }
        self.input_a_acciones = {
            "W": "UP",
            "S": "DOWN",
            "A": "LEFT",
            "D": "RIGHT",
            "B": "BLOWGUN",
            "E": "EXIT",
        }

        self.percepto = self.generar_percepto()
        self.jugando = True
        self.ejecutar_laberinto()

    def generar_estado_inicial(self):
        """
        Genera el estado inicial. Las trampas pueden compartor casilla, igual que CK, M y S, pero
        no se pueden mezclar. El inicio queda libre

        Returns:
            list: matriz que representa el estado del laberinto
        """
        base = [["    " for _ in range(self.tamaño)] for _ in range(self.tamaño)]
        base[0][0] = self.caracteres_Wilson
        for i in ["F   ", "P   ", "D   "]:
            x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            while [x, y] == [0, 0]:
                x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            if base[x][y] != "    ":
                merged = base[x][y].strip() + i.strip()
                base[x][y] = merged + " " * (4 - len(merged))
            else:
                base[x][y] = i
        for i in ["M   ", "CK  ", "S   "]:
            x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            while base[x][y] in ["F   ", "P   ", "D   "] or [x, y] == [0, 0]:
                x, y = [random.randint(0, self.tamaño - 1) for _ in range(2)]
            if base[x][y] != "    ":
                merged = base[x][y].strip() + i.strip()
                base[x][y] = merged + " " * (4 - len(merged))
            else:
                base[x][y] = i
        return base

    def generar_percepto(self):
        """
        Genera un percepto en base a la posición del jugador. Ese percepto es procesado
        por el agente bayesiano, que devuelve su prediccion.

        Returns:
            list: lista con información de los perceptos (orden de las diapositivas mas kurtz al final)
        """
        base = [0 for _ in range(11)]
        if self.pos[1] == 0:
            base[7] = 1
        elif self.pos[1] == self.tamaño - 1:
            base[8] = 1
        if self.pos[0] == 0:
            base[5] = 1
        elif self.pos[0] == self.tamaño - 1:
            base[6] = 1
        if self.grito:
            base[9] = 1
        if self.kurt_encontrado:
            base[10] = 1
        self.adyacentes = self.comprobar_adyacentes()
        for l in self.estado[self.pos[0]][self.pos[1]]:
            if l != " ":
                val = self.traduccion_a_perceptos.get(l, None)
                if val != None:
                    base[val] = 1
        for i in self.adyacentes:
            base[i] = 1
        self.agente.procesar_perceptos(base, self.pos)

        return base

    def elegir_mejor_casilla(self, matriz_probabilidades):
        """
        Algoritmo de greedy para elegir el siguiente movimiento. Dada la
        matriz de probabilidades escoje la casilla de la frontera con menos
        posibilidades de que el jugador muera

        Args:
            matriz_probabilidades (list): matriz con las probabilidades de los elementos para cada casilla

        Returns:
            tuple: el nodo al que queremos ir
        """
        # mirar implementacion del dardo
        prob_morir = lambda x: sum(
            i for i in x[:4]
        )  # suma de las 4 prob porque son disjuntas
        siguiente_mov = min(
            self.frontera, key=lambda x: prob_morir(matriz_probabilidades[x[0]][x[1]])
        )
        return siguiente_mov

    def comprobar_adyacentes(self):
        """
        Comprueba el contenido de las casillas adyacentes a la actual

        Returns:
            list: los contenidos de esas casillas
        """
        ady = []
        if self.pos[1] > 0:
            for l in self.estado[self.pos[0]][self.pos[1] - 1]:
                v = self.traduccion_a_perceptos.get(l, None)
                if v != None:
                    ady.append(v)

        if self.pos[1] < self.tamaño - 1:
            for l in self.estado[self.pos[0]][self.pos[1] + 1]:
                v = self.traduccion_a_perceptos.get(l, None)
                if v != None:
                    ady.append(v)

        if self.pos[0] > 0:
            for l in self.estado[self.pos[0] - 1][self.pos[1]]:
                v = self.traduccion_a_perceptos.get(l, None)
                if v != None:
                    ady.append(v)

        if self.pos[0] < self.tamaño - 1:
            for l in self.estado[self.pos[0] + 1][self.pos[1]]:
                v = self.traduccion_a_perceptos.get(l, None)
                if v != None:
                    ady.append(v)

        return ady

    def ejecutar_accion(self, accion):
        """
        Dada una acción la ejecuta

        Args:
            accion (str): la accion
        """
        pos_antes = self.pos.copy()
        if accion == "LEFT":
            if self.percepto[7] != 1:
                self.pos[1] -= 1
            else:
                print("No te puedes mover hacia la izquierda, hay una pared")
        elif accion == "RIGHT":
            if self.percepto[8] != 1:
                self.pos[1] += 1
            else:
                print("No te puedes mover hacia la derecha, hay una pared")
        elif accion == "UP":
            if self.percepto[5] != 1:
                self.pos[0] -= 1
            else:
                print("No te puedes mover hacia arriba, hay una pared")
        elif accion == "DOWN":
            if self.percepto[6] != 1:
                self.pos[0] += 1
            else:
                print("No te puedes mover hacia abajo, hay una pared")

        elif accion == "BLOWGUN":
            if self.dardo:
                a = b = -1
                while a not in range(0, self.tamaño) and b not in range(0, self.tamaño):
                    if a != -1 or b != -1:
                        print(
                            "El dardo se choca contra la pared, escoje otra direccion"
                        )
                    direccion = input(
                        "Elige la dirección del dardo, W (up), S (down), A (left) o D (right): "
                    )
                    while direccion.lower() not in ["w", "a", "s", "d"]:
                        direccion = input(
                            "Elige la dirección del dardo, W (up), S (down), A (left) o D (right): "
                        )
                    if direccion == "w":
                        a = self.pos[0] - 1
                        b = self.pos[1]
                    elif direccion == "s":
                        a = self.pos[0] + 1
                        b = self.pos[1]
                    elif direccion == "a":
                        a = self.pos[0]
                        b = self.pos[1] - 1
                    else:
                        a = self.pos[0]
                        b = self.pos[1] + 1
                if "M" in self.estado[a][b]:
                    self.grito = True
                    self.monstruo_muerto = True

                self.dardo = False
            else:
                print("No te quedan dardos")
        elif accion == "EXIT":
            if self.en_salida:
                if self.kurt_encontrado:
                    print("Enhorabuena, has escapado del laberinto")
                else:
                    print("Escapas del laberinto, pero dejas a Kurt abandonado")
                self.jugando = False
            else:
                print("No estás en la salida")
        if pos_antes != self.pos:
            texto = ""

            if self.en_salida:
                texto += "S"
                self.en_salida = False
            if self.en_monstruo:
                texto += "M"
                self.en_monstruo = False
            self.estado[pos_antes[0]][pos_antes[1]] = texto + " " * (4 - len(texto))
            if self.pos not in self.visitados:
                self.frontera.remove(tuple(self.pos))
            self.comprobaciones_tras_mover()
            self.estado[self.pos[0]][self.pos[1]] = self.caracteres_Wilson

    def sacar_adyacentes(self, f, c, visitadas):
        """
        Dada una fila y columna devuelve las casillas adyacentes que no
        se hayan visitado

        Args:
            f (int): fila
            c (int): columna
            visitadas (list): las casillas ya visitadas

        Returns:
            list: adyacentes no visitadas
        """
        adyacentes = []
        for x, y in [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]:
            if (
                x in range(0, self.tamaño)
                and y in range(0, self.tamaño)
                and [x, y] not in visitadas
            ):
                adyacentes.append((x, y))

        return adyacentes

    def comprobaciones_tras_mover(self):
        """
        Comprueba que debe ocurrir tras el movimiento del jugador
        """
        lista_casilla = []
        for l in self.estado[self.pos[0]][self.pos[1]]:
            if l != " ":
                lista_casilla.append(self.traduccion_a_perceptos.get(l, None))
        for contenido_casilla in lista_casilla:
            if contenido_casilla in [0, 1, 2, 3]:
                if not self.monstruo_muerto:
                    self.jugando = False
                if contenido_casilla == 0:
                    print("Te has quemado en la trampa de fuego. Misión fallida")
                elif contenido_casilla == 1:
                    print("Has caido en la trampa de pinchos. Misión fallida")
                elif contenido_casilla == 2:
                    print("Has caido en la trampa de dardos. Misión fallida")
                elif not self.monstruo_muerto:
                    print("El monstruo te ha comido. Misión fallida")
                else:
                    self.en_monstruo = True
                    print("Ves el cadáver del monstruo")
            elif contenido_casilla == 4:
                self.en_salida = True
                if self.busqueda:
                    self.busqueda.pos_salida = self.pos.copy()
                print("Estas en la salida")
            elif self.estado[self.pos[0]][self.pos[1]] == "CK  ":
                self.kurt_encontrado = True
                if self.busqueda:
                    self.busqueda.kurt_encontrado = True
                self.caracteres_Wilson = "CWCK"

        if self.pos not in self.visitados:
            self.visitados.append(self.pos.copy())
        for i in self.sacar_adyacentes(self.pos[0], self.pos[1], self.visitados):
            if i not in self.frontera + self.pos:
                self.frontera.append(i)
        self.percepto = self.generar_percepto()

    def ejecutar_laberinto(self):
        """
        Ejecuta el laberinto
        """
        print("Bienvenido al laberinto")
        print(
            "Las acciones disponibles son: W (up), S (down), A (left), D (right), E (exit) y B (blowdart)"
        )
        while self.jugando:
            print(str(self))
            casilla = self.elegir_mejor_casilla(self.agente.matriz_probabilidades)

            print(
                f"La mejor casilla a la que avanzar es: ({casilla[0]+1}, {casilla[1]+1})"
            )
            if not self.busqueda:
                accion = self.pedir_accion()
            else:
                accion = self.busqueda.give_next_move(
                    self.agente.matriz_probabilidades,
                    self.pos,
                    self.visitados,
                )
                time.sleep(0.05)
            self.ejecutar_accion(accion)
