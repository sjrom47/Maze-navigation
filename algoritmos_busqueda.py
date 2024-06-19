"""
Trabajo final fundamentos inteligencia artificial Sergio Jiménez Romero
"""


class AlgoritmosBusqueda:
    """
    Clase base que contiene distaintos algoritmos de búsqueda y funciones de apoyo
    """

    def __init__(self, n) -> None:
        """
        Constructor de la clase

        Args:
            n (int): el tamaño del laberinto
        """
        self.n = n
        self.frontera = []
        self.generated_moves = []

    def elegir_mov_bfs(self, seguras):
        """
        Elige el siguiente movimiento mediante el algoritmo de BFS. Se coge primero de
        las casillas seguras y luego una del resto

        Args:
            seguras (list): casillas seguras

        Returns:
            tuple: la casilla destino
        """
        lista_seguras = [(x, y) for x, y in self.frontera if [x, y] in seguras]
        if lista_seguras != []:
            siguiente_mov = lista_seguras[0]

        else:
            siguiente_mov = self.frontera[0]
        return siguiente_mov

    def a_star_en_conocidos(self, inicio, destino, visitadas):
        """
        Encuentra el camino más corto de una casilla visitada a otra mediante
        el algoritmo de A*

        Args:
            inicio (tuple): casilla de salida
            destino (tuple): destino
            visitadas (list): las casillas por las que nos podemos desplazar

        Returns:
            list: camino al destino
        """
        f_score = lambda x: abs(x[0] - destino[0]) + abs(x[1] - destino[1])
        valores = {inicio: f_score(inicio)}

        padres = {}
        costes = {inicio: 0}

        while valores:
            nodo_actual = min(valores, key=lambda x: valores[x])

            del valores[nodo_actual]

            if (
                destino
                in self.sacar_adyacentes(nodo_actual[0], nodo_actual[1], visitadas)
                or destino == nodo_actual
            ):
                camino = []
                while nodo_actual in padres:
                    camino.append(nodo_actual)
                    nodo_actual = padres[nodo_actual]

                return camino[::-1]
            ady_visitadas = self.sacar_adyacentes_visitadas(
                nodo_actual[0], nodo_actual[1], visitadas
            )
            for vecino in ady_visitadas:
                valor_hipotetico = costes[nodo_actual] + 1 + f_score(vecino)
                if tuple(vecino) not in costes or valor_hipotetico < valores.get(
                    tuple(vecino), -1
                ):
                    valores[tuple(vecino)] = valor_hipotetico
                    costes[tuple(vecino)] = costes[tuple(nodo_actual)] + 1
                    padres[tuple(vecino)] = nodo_actual

        return None

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
                x in range(0, self.n)
                and y in range(0, self.n)
                and [x, y] not in visitadas
            ):
                adyacentes.append((x, y))

        return adyacentes

    def sacar_adyacentes_visitadas(self, f, c, visitadas):
        """
        Dada una fila y columna obtiene las adyacentes que hayan sido visitadas

        Args:
            f (int): fila
            c (int): columna
            visitadas (list): casillas visitadas

        Returns:
            list: adyacentes vistadas
        """
        adyacentes_visitadas = []
        for x, y in [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]:
            if (
                x in range(0, self.n)
                and y in range(0, self.n)
                and [x, y] in visitadas
                and [x, y] != [f, c]
            ):
                adyacentes_visitadas.append([x, y])
        return adyacentes_visitadas

    def pasar_a_acciones(self, lista_nodos, pos):
        """
        Dada una lista de nodos, obtiene las acciones correspondientes para desplazarse
        por esos nodos en ese orden

        Args:
            lista_nodos (list): lista de los nodos por los que nos queremos desplazar
            pos (tuple): posicion inicial

        Returns:
            list: lista de acciones
        """
        resta = lambda x, y: (y[0] - x[0], y[1] - x[1])
        acciones = {
            (1, 0): "UP",
            (-1, 0): "DOWN",
            (0, 1): "LEFT",
            (0, -1): "RIGHT",
            (0, 0): "EXIT",
        }
        lista_acciones = []
        nodo_actual = pos
        for nodo in lista_nodos:
            lista_acciones.append(acciones[resta(nodo, nodo_actual)])
            nodo_actual = nodo
        return lista_acciones

    def elegir_movs_greedy(self, matriz_probabilidades):
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


class BusquedaLogica(AlgoritmosBusqueda):
    """
    Busqueda en el laberinto logico
    """

    def __init__(self, n=6) -> None:
        """
        Constructor de la clase

        Args:
            n (int, optional): tamaño del laberinto. Defaults to 6.
        """
        super().__init__(n)
        self.kurt_encontrado = False
        self.pos_salida = []
        self.destino_anterior = None

    def give_next_move(self, seguras, pos, visitadas):
        """
        Obtiene el siguiente movimiento. Si hay movimientos generados devuelve
        el siguiente, de lo contrario genera los siguientes movimientos

        Args:
            seguras (list): casillas seguras
            pos (list): posicion del jugador
            visitadas (list): casillas visitadas

        Returns:
            str: la acción que se debe ejecutar
        """
        for i in self.sacar_adyacentes(pos[0], pos[1], visitadas):
            if i not in self.frontera + pos:
                self.frontera.append(i)
        if (
            self.kurt_encontrado
            and self.pos_salida != []
            and self.generated_moves == []
        ):  # si hemos encontrado a kurtz y la salida nos vamos a la salida directamente y salimos del laberinto
            if self.pos_salida != pos:
                camino = self.a_star_en_conocidos(
                    tuple(pos), tuple(self.pos_salida), visitadas
                )
            else:
                camino = [tuple(self.pos_salida)]
            self.generated_moves = self.pasar_a_acciones(camino, pos) + ["EXIT"]

        elif self.generated_moves == []:  # Generamos nuevos movimientos
            if self.destino_anterior:
                self.frontera.remove(tuple(self.destino_anterior))
            camino = []
            destino_final = self.elegir_mov_bfs(seguras)
            if destino_final not in self.sacar_adyacentes(pos[0], pos[1], visitadas):
                camino = self.a_star_en_conocidos(
                    tuple(pos), tuple(destino_final), visitadas
                )

            self.generated_moves = self.pasar_a_acciones(camino + [destino_final], pos)
            self.destino_anterior = destino_final
        move = self.generated_moves.pop(0)
        print(move)
        return move


class BusquedaBayesiana(AlgoritmosBusqueda):
    """
    Clase de la busqueda bayesiana
    """

    def __init__(self, n=6) -> None:
        """
        Constructor de la clase

        Args:
            n (int, optional): El tamaño del laberinto. Defaults to 6.
        """
        super().__init__(n)
        self.kurt_encontrado = False
        self.pos_salida = []
        self.destino_anterior = None

    def give_next_move(self, matriz_probabilidades, pos, visitadas):
        """
        Obtiene el siguiente movimiento. Si hay movimientos generados devuelve
        el siguiente, de lo contrario genera los siguientes movimientos

        Args:
            matriz_probabilidades (list): matriz con las probabilidades de la presencia de cada elemento
            pos (list): posicion del jugador
            visitadas (list): casillas visitadas

        Returns:
            str: siguiente acción
        """
        for i in self.sacar_adyacentes(pos[0], pos[1], visitadas):
            if i not in self.frontera + pos:
                self.frontera.append(i)
        if (
            self.kurt_encontrado
            and self.pos_salida != []
            and self.generated_moves == []
        ):
            if self.pos_salida != pos:
                camino = self.a_star_en_conocidos(
                    tuple(pos), tuple(self.pos_salida), visitadas
                )
            else:
                camino = [tuple(self.pos_salida)]
            self.generated_moves = self.pasar_a_acciones(camino, pos) + ["EXIT"]

        elif self.generated_moves == []:
            if self.destino_anterior:
                self.frontera.remove(tuple(self.destino_anterior))
            camino = []
            destino_final = self.elegir_movs_greedy(matriz_probabilidades)
            if destino_final not in self.sacar_adyacentes(pos[0], pos[1], visitadas):
                camino = self.a_star_en_conocidos(
                    tuple(pos), tuple(destino_final), visitadas
                )

            self.generated_moves = self.pasar_a_acciones(camino + [destino_final], pos)
            self.destino_anterior = destino_final
        move = self.generated_moves.pop(0)
        print(move)
        return move
