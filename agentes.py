import pycosat
from itertools import product

"""
Trabajo final fundamentos inteligencia artificial de Sergio Jiménez Romero
"""

LOGICTRACE = False


class Logic:
    """
    Esta clase esta basada en el ejemplo proporcionado por Juan Claudio Agüi sobre pycosat
    """

    def __init__(self) -> None:
        self.kb = []
        self.symbols = []

    def clean(self):
        self.kb = []
        self.symbols = []

    def to_number(self, symbol):
        if symbol[0] == "-":
            sign = -1
            symbol = symbol[1:]
        else:
            sign = 1

        if symbol in self.symbols:
            return (self.symbols.index(symbol) + 1) * sign
        else:
            self.symbols.append(symbol)
            return len(self.symbols) * sign

    def process_clause(self, clause):
        """
        takes a list as a collection of signed literals, and results in DIMACS format clause, signed integer list
        that represents the clause
        """
        # a clause is a list of ors
        l_clause = [clause] if not isinstance(clause, list) else clause
        numClause = [self.to_number(symbol) for symbol in l_clause]
        return numClause

    def dimacs_to_symbol(self, dimacs):
        """from dimacs to symbols based clause"""
        clause = []
        for i in dimacs:
            symbol = f"{'-' if i < 0 else ''}{self.symbols[abs(i)-1]}"
            clause.append(symbol)
        return clause

    def negate_dimacs(self, dimacs):
        return [[-i] for i in dimacs]

    def add_to_kb(self, clause):
        """
        adds the clause to the KB,  clause is a list of signed literals
        """
        l_clause = [clause] if not isinstance(clause, list) else clause
        dimacs = self.process_clause(l_clause)
        # avoid repetition of clauses
        if dimacs not in self.kb:
            if LOGICTRACE:
                print(f"Adding {l_clause} converted as {dimacs} to the KB")
            self.kb.append(dimacs)

    def add_clause_list_to_kb(self, clauseList):
        """
        adds the list of clauses to the KB,  each clause is a list of signed literals
        """
        for clause in clauseList:
            self.add_to_kb(clause)

    def dumpKB(self):
        """prints the kB in a readable, symbolic form"""
        print(f"There are {len(self.kb)} clauses with {len(self.symbols)} symbols")
        for i, dimacs in enumerate(self.kb):
            print(f"#{i}: {dimacs} ==> {self.dimacs_to_symbol(dimacs)}")

    def dump_kb_to_file(self, fn):
        """
        writes content of dumpKB to a named file
        """
        with open(fn, mode="w") as f:
            for i, dimacs in enumerate(self.kb):
                f.write(f"#{i}: {dimacs} ==> {self.dimacs_to_symbol(dimacs)}\n")

    def ask_kb(self, clause, verbose=False):
        """
        returns True if the current KB, augmented by the negation of the given clause, proves UNSAT
        which means the current KB entails the given clause
        """
        qKB = [dim for dim in self.kb]
        dimacsClause = self.process_clause(clause)
        negated = self.negate_dimacs(dimacsClause)
        for d in negated:
            qKB.append(d)
        answer = pycosat.solve(qKB)
        if LOGICTRACE:
            print(
                f"Qestion for negation of  {clause}  answers {answer} and so {clause} is {answer=='UNSAT'}"
            )
        return answer == "UNSAT"

    def check_kb_vs_clause_set(self, clauses):
        """
        return False if adding the set of clauses makes the KB UNSAT,
        True otherwise

        Does not modify current KB

        """

        qKB = [dim for dim in self.kb]
        for clause in clauses:
            dimacsClause = self.process_clause(clause)
            qKB.append(dimacsClause)
        answer = pycosat.solve(qKB)
        comp = not (answer == "UNSAT")
        # print (f" CHECK Clauses {clauses} are  {'SI' if comp else 'NOT'} COMPATIBLE with KB")
        return comp

    def allModelsforKB(self):
        """Returns a list atoms that satisfy the KB
        Beware, this is not a generator, but a list. It may produce a combinatorial explosion.
        Be carefull
        """
        return [self.dimacs_to_symbol(sol) for sol in pycosat.itersolve(self.kb)]


class AgenteLogico:
    """
    Este es el agente que nos ayuda en el laberinto lógico
    """

    def __init__(self, n) -> None:
        """
        Este es el constructor de nuestro agente lógico. Creamos una instancia de la clase Logic
        para que pueda razonar sobre la información que le llega y añadimos las condiciones iniciales

        Args:
            n (int): la dimensión del tablero
        """
        self.logic = Logic()
        self.n = n
        self.precipicio_max = False
        self.precipicios_enc = 0
        self.añadir_condiciones_iniciales()

    def añadir_condiciones_iniciales(self):
        """
        Añadimos las condiciones iniciales a la KB. Estas conddiciones son que:
        - Hay estímulo si y solo si la causa se encuentra en una casilla adyacente
        - No hay dos causas en la misma casilla
        - No hay más de una instancia de cada causa (excepto precicpicios)

        S representa salida, M monstruo y P precipicio. Una E deleante siginfica que es el estímulo
        """
        estimulos = ["EP", "EM", "ES"]
        causas = ["P", "M", "S"]
        initial_clause_list = []
        tiles = [i for i in product(list(range(self.n)), repeat=2)]

        for _ in range(len(tiles)):
            x, y = tiles.pop(0)
            for estimulo, causa in zip(estimulos, causas):
                ady = []
                if x > 0:
                    ady.append(f"{causa}{x-1}{y}")
                if x < self.n - 1:
                    ady.append(f"{causa}{x+1}{y}")
                if y > 0:
                    ady.append(f"{causa}{x}{y-1}")
                if y < self.n - 1:
                    ady.append(f"{causa}{x}{y+1}")
                initial_clause_list.append([f"-{estimulo}{x}{y}"] + ady)
                initial_clause_list.extend(
                    [
                        [f"{estimulo}{x}{y}", f"-{ady[i]}"] for i in range(len(ady))
                    ]  # estímulo y causa
                )
                if causa != "P":
                    for i in tiles:
                        initial_clause_list.append(
                            [f"-{causa}{x}{y}", f"-{causa}{i[0]}{i[1]}"]  # exclusión
                        )

            initial_clause_list.append(
                [f"-M{x}{y}", f"-P{x}{y}"]
            )  # No comparten casillas
            initial_clause_list.append([f"-M{x}{y}", f"-S{x}{y}"])
            initial_clause_list.append([f"-S{x}{y}", f"-P{x}{y}"])

        self.logic.add_clause_list_to_kb(initial_clause_list)

    def process_percept(
        self, percept, position, casillas_conocidas, en_salida, en_monstruo
    ):
        """
        Dado un percepto, la posición del jugador y las casillas conocidas vemos si
        el modelo ha sido capaz de extraer alguna información adicional

        Args:
            percept (list): lista de 1s y 0s con información sobre los perceptos
            position (list): posición del jugador en el laberinto
            casillas_conocidas (list): lista con las casillas de las que se sabe su contenido
            en_salida (bool): si el jugador está en la salida
            en_monstruo (bool): si el jugador está en el monstruo

        Returns:
            list, list, list, list: listas con las casillas cuyo contenido se ha averiguado
                                    (nada, monstruo, precipicio y salida en ese orden)
        """
        seguras = []
        monstruo = []
        precipicio = []
        salida = []
        percept_dict = {0: "EP", 1: "EM", 2: "ES"}
        for ind, i in enumerate(percept[:3]):
            estimulo = percept_dict.get(ind, "G")
            if i == 1:
                self.logic.add_to_kb([f"{estimulo}{position[0]}{position[1]}"])
            elif ind < 3:
                self.logic.add_to_kb([f"-{estimulo}{position[0]}{position[1]}"])
        # No hay precipicio en la casilla actual o el jugador estaría muerto

        if not en_monstruo:
            self.logic.add_to_kb([f"-M{position[0]}{position[1]}"])
        self.logic.add_to_kb([f"-P{position[0]}{position[1]}"])
        if not en_salida:
            self.logic.add_to_kb([f"-S{position[0]}{position[1]}"])
        for i in product(list(range(self.n)), repeat=2):
            # Preguntamos al modelo si sabe lo que hay en cada una de las casillas
            if list(i) not in casillas_conocidas:
                if self.precipicio_max:
                    self.logic.add_to_kb([f"-P{i[0]}{i[1]}"])
                m, p, s = [
                    self.logic.ask_kb(f"M{i[0]}{i[1]}"),
                    self.logic.ask_kb(f"P{i[0]}{i[1]}"),
                    self.logic.ask_kb(f"S{i[0]}{i[1]}"),
                ]
                if m:  # monstruo
                    monstruo.append(list(i))
                elif p:  # precipicio
                    precipicio.append(list(i))
                elif s:  # salida
                    salida.append(list(i))
            else:
                # Vemos si las casillas adyacentes son seguras
                #
                # (solo las adyacentes porque son de las unicas que podemos ahber recibido un estimulo)
                ady = []
                if i[0] > 0:
                    if [i[0] - 1, i[1]] not in casillas_conocidas:
                        ady.append([i[0] - 1, i[1]])
                if i[0] < self.n - 1:
                    if [i[0] + 1, i[1]] not in casillas_conocidas:
                        ady.append([i[0] + 1, i[1]])
                if i[1] > 0:
                    if [i[0], i[1] - 1] not in casillas_conocidas:
                        ady.append([i[0], i[1] - 1])
                if i[1] < self.n - 1:
                    if [i[0], i[1] + 1] not in casillas_conocidas:
                        ady.append([i[0], i[1] + 1])
                for x, y in ady:
                    nm, np, ns = [
                        self.logic.ask_kb(f"-M{x}{y}"),
                        self.logic.ask_kb(f"-P{x}{y}"),
                        self.logic.ask_kb(f"-S{x}{y}"),
                    ]
                    # Si no hay ninguno de esos tres elementos es que es 'segura'
                    if nm and np and ns:
                        seguras.append([x, y])
        self.precipicios_enc += len(precipicio)
        if self.precipicios_enc == 3:
            self.precipicio_max = True
            self.precipicios_enc = 0
        if self.precipicio_max:
            self.precipicio_max = False
        return seguras, monstruo, precipicio, salida


class AgenteBayesiano:
    """
    Esta es la clase del agente que te ayuda en el laberinto bayesiano
    """

    def __init__(self, n) -> None:
        """
        Inicializamos la matriz de probabilidades a que todo es 1/n**2-1 excepto la inicial que
        es todo 0 porque no puede haber nada en la inicial

        Args:
            n (int): el tamaño del laberinto
        """
        self.matriz_probabilidades = [
            [[1 / (n**2 - 1) for _ in range(5)] for _ in range(n)] for _ in range(n)
        ]
        self.matriz_probabilidades[0][0] = [0 for _ in range(5)]
        self.n = n

    def procesar_perceptos(self, percepto_0, position):
        """
        Para cada casilla y para cada causa actualizamos las probabilidades
        en función de los perceptos que hemos recibido

        Args:
            percepto_0 (list): lista de 1s y 0s con los perceptos
            position (list): la posición del jugador
        """
        percepto = percepto_0.copy()
        percepto = percepto[:5]

        adyacentes = self.sacar_adyacentes(position[0], position[1])
        for ind, i in enumerate(percepto):
            prob_en_ady = self.prob_causa_en_adyacentes(adyacentes, ind)
            for fnd, fila in enumerate(self.matriz_probabilidades):
                for cnd, casilla in enumerate(fila):
                    if i:
                        # hay estímulo
                        likelihood = 1 if [fnd, cnd] in adyacentes else 0
                        casilla[ind] = likelihood * casilla[ind] / prob_en_ady  # bayes
                    else:
                        # no hay estímulo
                        likelihood = 1 if [fnd, cnd] not in adyacentes else 0
                        casilla[ind] = (
                            likelihood * casilla[ind] / (1 - prob_en_ady)
                        )  # bayes

    def sacar_adyacentes(self, f, c):
        """
        Dada una fila y una columna devuelve una lista con las adyacentes y la propia casilla

        Args:
            f (int): fila
            c (int): columna

        Returns:
            list: lista con las adyacentes y la propia casilla
        """
        adyacentes = [[f, c]]
        for x, y in [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]:
            if x in range(0, self.n) and y in range(0, self.n):
                adyacentes.append([x, y])
        return adyacentes

    def prob_causa_en_adyacentes(self, adyacentes, ind):
        """
        Devuelve la probabilidad de que una causa se encuentre en una casilla o sus adyacentes

        Args:
            adyacentes (list): la casilla y sus adyacentes
            ind (int): cual es el elemento del que se esta calculando la probabilidad

        Returns:
            float: la probabilidad buscada
        """
        suma = 0
        for x, y in adyacentes:
            suma += self.matriz_probabilidades[x][y][ind]
        return suma
