import pycosat
from itertools import product


LOGICTRACE = False


class Logic:
    """
    Logical agent class
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
        Takes a list as a collection of signed literals, and results in DIMACS format clause, signed integer list
        that represents the clause
        """
        # A clause is a list of ORs
        l_clause = [clause] if not isinstance(clause, list) else clause
        numClause = [self.to_number(symbol) for symbol in l_clause]
        return numClause

    def dimacs_to_symbol(self, dimacs):
        """From DIMACS to symbols based clause"""
        clause = []
        for i in dimacs:
            symbol = f"{'-' if i < 0 else ''}{self.symbols[abs(i)-1]}"
            clause.append(symbol)
        return clause

    def negate_dimacs(self, dimacs):
        return [[-i] for i in dimacs]

    def add_to_kb(self, clause):
        """
        Adds the clause to the KB, clause is a list of signed literals
        """
        l_clause = [clause] if not isinstance(clause, list) else clause
        dimacs = self.process_clause(l_clause)
        # Avoid repetition of clauses
        if dimacs not in self.kb:
            if LOGICTRACE:
                print(f"Adding {l_clause} converted as {dimacs} to the KB")
            self.kb.append(dimacs)

    def add_clause_list_to_kb(self, clauseList):
        """
        Adds the list of clauses to the KB, each clause is a list of signed literals
        """
        for clause in clauseList:
            self.add_to_kb(clause)

    def dumpKB(self):
        """Prints the KB in a readable, symbolic form"""
        print(f"There are {len(self.kb)} clauses with {len(self.symbols)} symbols")
        for i, dimacs in enumerate(self.kb):
            print(f"#{i}: {dimacs} ==> {self.dimacs_to_symbol(dimacs)}")

    def dump_kb_to_file(self, fn):
        """
        Writes content of dumpKB to a named file
        """
        with open(fn, mode="w") as f:
            for i, dimacs in enumerate(self.kb):
                f.write(f"#{i}: {dimacs} ==> {self.dimacs_to_symbol(dimacs)}\n")

    def ask_kb(self, clause, verbose=False):
        """
        Returns True if the current KB, augmented by the negation of the given clause, proves UNSAT
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
                f"Question for negation of {clause} answers {answer} and so {clause} is {answer=='UNSAT'}"
            )
        return answer == "UNSAT"

    def check_kb_vs_clause_set(self, clauses):
        """
        Return False if adding the set of clauses makes the KB UNSAT,
        True otherwise

        Does not modify current KB
        """
        qKB = [dim for dim in self.kb]
        for clause in clauses:
            dimacsClause = self.process_clause(clause)
            qKB.append(dimacsClause)
        answer = pycosat.solve(qKB)
        comp = not (answer == "UNSAT")
        return comp

    def allModelsforKB(self):
        """Returns a list of atoms that satisfy the KB
        Beware, this is not a generator, but a list. It may produce a combinatorial explosion.
        Be careful
        """
        return [self.dimacs_to_symbol(sol) for sol in pycosat.itersolve(self.kb)]


class LogicalAgent:
    """
    This is the agent that helps us in the logical maze
    """

    def __init__(self, n) -> None:
        """
        This is the constructor of our logical agent. We create an instance of the Logic class
        so that it can reason about the information it receives and add the initial conditions

        Args:
            n (int): the dimension of the board
        """
        self.logic = Logic()
        self.n = n
        self.max_precipice = False
        self.found_precipices = 0
        self.add_initial_conditions()

    def add_initial_conditions(self):
        """
        We add the initial conditions to the KB. These conditions are that:
        - There is a stimulus if and only if the cause is in an adjacent cell
        - There are no two causes in the same cell
        - There is no more than one instance of each cause (except precipices)

        S represents exit, M monster, and P precipice. An E in front means it is the stimulus
        """
        stimuli = ["EP", "EM", "ES"]
        causes = ["P", "M", "S"]
        initial_clause_list = []
        tiles = [i for i in product(list(range(self.n)), repeat=2)]

        for _ in range(len(tiles)):
            x, y = tiles.pop(0)
            for stimulus, cause in zip(stimuli, causes):
                adj = []
                if x > 0:
                    adj.append(f"{cause}{x-1}{y}")
                if x < self.n - 1:
                    adj.append(f"{cause}{x+1}{y}")
                if y > 0:
                    adj.append(f"{cause}{x}{y-1}")
                if y < self.n - 1:
                    adj.append(f"{cause}{x}{y+1}")
                initial_clause_list.append([f"-{stimulus}{x}{y}"] + adj)
                initial_clause_list.extend(
                    [
                        [f"{stimulus}{x}{y}", f"-{adj[i]}"] for i in range(len(adj))
                    ]  # stimulus and cause
                )
                if cause != "P":
                    for i in tiles:
                        initial_clause_list.append(
                            [f"-{cause}{x}{y}", f"-{cause}{i[0]}{i[1]}"]  # exclusion
                        )

            initial_clause_list.append([f"-M{x}{y}", f"-P{x}{y}"])  # Do not share cells
            initial_clause_list.append([f"-M{x}{y}", f"-S{x}{y}"])
            initial_clause_list.append([f"-S{x}{y}", f"-P{x}{y}"])

        self.logic.add_clause_list_to_kb(initial_clause_list)

    def process_percept(self, percept, position, known_cells, at_exit, at_monster):
        """
        Given a percept, the player's position, and the known cells, we see if
        the model has been able to extract any additional information

        Args:
            percept (list): list of 1s and 0s with information about the percepts
            position (list): player's position in the maze
            known_cells (list): list of cells whose content is known
            at_exit (bool): if the player is at the exit
            at_monster (bool): if the player is at the monster

        Returns:
            list, list, list, list: lists with the cells whose content has been discovered
                                    (nothing, monster, precipice, and exit in that order)
        """
        safe = []
        monster = []
        precipice = []
        exit = []
        percept_dict = {0: "EP", 1: "EM", 2: "ES"}
        for ind, i in enumerate(percept[:3]):
            stimulus = percept_dict.get(ind, "G")
            if i == 1:
                self.logic.add_to_kb([f"{stimulus}{position[0]}{position[1]}"])
            elif ind < 3:
                self.logic.add_to_kb([f"-{stimulus}{position[0]}{position[1]}"])
        # No precipice in the current cell or the player would be dead

        if not at_monster:
            self.logic.add_to_kb([f"-M{position[0]}{position[1]}"])
        self.logic.add_to_kb([f"-P{position[0]}{position[1]}"])
        if not at_exit:
            self.logic.add_to_kb([f"-S{position[0]}{position[1]}"])
        for i in product(list(range(self.n)), repeat=2):
            # We ask the model if it knows what is in each of the cells
            if list(i) not in known_cells:
                if self.max_precipice:
                    self.logic.add_to_kb([f"-P{i[0]}{i[1]}"])
                m, p, s = [
                    self.logic.ask_kb(f"M{i[0]}{i[1]}"),
                    self.logic.ask_kb(f"P{i[0]}{i[1]}"),
                    self.logic.ask_kb(f"S{i[0]}{i[1]}"),
                ]
                if m:  # monster
                    monster.append(list(i))
                elif p:  # precipice
                    precipice.append(list(i))
                elif s:  # exit
                    exit.append(list(i))
            else:
                # We see if the adjacent cells are safe
                #
                # (only the adjacent ones because they are the only ones from which we could have received a stimulus)
                adj = []
                if i[0] > 0:
                    if [i[0] - 1, i[1]] not in known_cells:
                        adj.append([i[0] - 1, i[1]])
                if i[0] < self.n - 1:
                    if [i[0] + 1, i[1]] not in known_cells:
                        adj.append([i[0] + 1, i[1]])
                if i[1] > 0:
                    if [i[0], i[1] - 1] not in known_cells:
                        adj.append([i[0], i[1] - 1])
                if i[1] < self.n - 1:
                    if [i[0], i[1] + 1] not in known_cells:
                        adj.append([i[0], i[1] + 1])
                for x, y in adj:
                    nm, np, ns = [
                        self.logic.ask_kb(f"-M{x}{y}"),
                        self.logic.ask_kb(f"-P{x}{y}"),
                        self.logic.ask_kb(f"-S{x}{y}"),
                    ]
                    # If there is none of those three elements, it is 'safe'
                    if nm and np and ns:
                        safe.append([x, y])
        self.found_precipices += len(precipice)
        if self.found_precipices == 3:
            self.max_precipice = True
            self.found_precipices = 0
        if self.max_precipice:
            self.max_precipice = False
        return safe, monster, precipice, exit


class BayesianAgent:
    """
    This is the class of the agent that helps you in the Bayesian maze
    """

    def __init__(self, n) -> None:
        """
        We initialize the probability matrix so that everything is 1/n**2-1 except the initial one which
        is all 0 because there can be nothing in the initial one

        Args:
            n (int): the size of the maze
        """
        self.probability_matrix = [
            [[1 / (n**2 - 1) for _ in range(5)] for _ in range(n)] for _ in range(n)
        ]
        self.probability_matrix[0][0] = [0 for _ in range(5)]
        self.n = n

    def process_percepts(self, percept_0, position):
        """
        For each cell and for each cause we update the probabilities
        based on the percepts we have received

        Args:
            percept_0 (list): list of 1s and 0s with the percepts
            position (list): the player's position
        """
        percept = percept_0.copy()
        percept = percept[:5]

        adjacents = self.get_adjacents(position[0], position[1])
        for ind, i in enumerate(percept):
            prob_in_adj = self.prob_cause_in_adjacents(adjacents, ind)
            for fnd, row in enumerate(self.probability_matrix):
                for cnd, cell in enumerate(row):
                    if i:
                        # there is a stimulus
                        likelihood = 1 if [fnd, cnd] in adjacents else 0
                        cell[ind] = likelihood * cell[ind] / prob_in_adj  # bayes
                    else:
                        # there is no stimulus
                        likelihood = 1 if [fnd, cnd] not in adjacents else 0
                        cell[ind] = likelihood * cell[ind] / (1 - prob_in_adj)  # bayes

    def get_adjacents(self, f, c):
        """
        Given a row and a column, returns a list with the adjacent cells and the cell itself

        Args:
            f (int): row
            c (int): column

        Returns:
            list: list with the adjacent cells and the cell itself
        """
        adjacents = [[f, c]]
        for x, y in [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]:
            if x in range(0, self.n) and y in range(0, self.n):
                adjacents.append([x, y])
        return adjacents

    def prob_cause_in_adjacents(self, adjacents, ind):
        """
        Returns the probability that a cause is in a cell or its adjacents

        Args:
            adjacents (list): the cell and its adjacents
            ind (int): which element the probability is being calculated for

        Returns:
            float: the sought probability
        """
        sum = 0
        for x, y in adjacents:
            sum += self.probability_matrix[x][y][ind]
        return sum
