import random
from agents import LogicalAgent, BayesianAgent
from search_algorithms import LogicalSearch, BayesianSearch
import time

"""
Final project for Artificial Intelligence Fundamentals by Sergio Jimenez Romero
"""


class BaseMaze:
    """
    Class with common functions for both mazes
    """

    def __init__(self, n, sol) -> None:
        """
        Class constructor

        Args:
            n (int): size of the maze
            sol (bool): whether to show the solved maze
        """
        self.sol = sol
        self.size = n
        self.Wilson_characters = "CW  "
        self.kurt_found = False
        self.safe_cells = []

        self.pos = [0, 0]
        self.visited = [self.pos.copy()]
        self.viewed = [self.pos.copy()]
        self.at_exit = False
        self.at_monster = False
        self.monster_dead = False

        self.scream = False

    def __str__(self) -> str:
        """
        Maze representation

        Returns:
            str: the representation of the maze state
        """
        result = ""
        for x, row in enumerate(self.state):
            result += "-----" * self.size + "\n"
            for i, j in zip(range(0, 3, 2), range(1, 4, 2)):
                for y, cell in enumerate(row):
                    result += (
                        f"|{cell[i]} {cell[j]}|"
                        if [x, y] in self.visited or self.sol or [x, y] in self.viewed
                        else "|? ?|"
                    )
                result += "\n"
        result += "-----" * self.size + "\n"
        for i in self.adjacents:
            result += self.messages[i] + " "
        if self.scream:
            result = result.replace("You smell something", self.messages[5])
        return result

    def request_action(self):
        """
        Requests an action from the player

        Returns:
            str: the chosen action
        """
        inp = input("Enter an action: ")
        action = self.input_to_actions.get(inp.upper(), None)
        while not action:
            print("An invalid action has been entered")
            inp = input("Enter an action: ")
            action = self.input_to_actions.get(inp.upper(), None)
        return action


class LogicalMaze(BaseMaze):
    """
    Class that creates and manages the logical maze
    """

    def __init__(self, n=6, sol=False, auto=False) -> None:
        """
        Logical maze constructor

        Args:
            n (int, optional): size of the maze. Defaults to 6.
            sol (bool, optional): whether to show it solved or not. Defaults to False.
            auto (bool, optional): whether to run the search algorithm. Defaults to False.
        """
        super().__init__(n, sol)
        self.search = None
        if auto:
            self.search = LogicalSearch(n)

        self.state = self.generate_initial_state()

        self.grenade = True

        self.percepts_translation = {"P   ": 0, "M   ": 1, "S   ": 2}
        self.messages = {
            0: "There is a breeze",
            1: "You smell something",
            2: "You see a light",
            5: "You hear a scream",
        }
        self.input_to_actions = {
            "W": "UP",
            "S": "DOWN",
            "A": "LEFT",
            "D": "RIGHT",
            "G": "GRENADE",
            "E": "EXIT",
        }
        self.agent = LogicalAgent(n)
        self.playing = True
        self.percept = self.generate_percept()

        self.run_maze()

    def generate_initial_state(self):
        """
        Generates the initial state of the maze

        Returns:
            list: matrix representing the maze
        """
        base = [["    " for _ in range(self.size)] for _ in range(self.size)]
        base[0][0] = self.Wilson_characters
        for i in ["P   ", "P   ", "P   ", "M   ", "CK  ", "S   "]:
            x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            while base[x][y] != "    ":
                x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            base[x][y] = i
        return base

    def generate_percept(self):
        """
        Generates a percept based on the player's position. This percept is processed
        by the logical agent, which returns its predictions. These are verified and stored
        according to their type

        Returns:
            list: list with percept information (order of slides plus Kurtz at the end)
        """
        base = [0 for _ in range(9)]
        if self.pos[1] == 0:
            base[5] = 1
        elif self.pos[1] == self.size - 1:
            base[6] = 1
        if self.pos[0] == 0:
            base[3] = 1
        elif self.pos[0] == self.size - 1:
            base[4] = 1
        if self.scream:
            base[7] = 1
        if self.kurt_found:
            base[8] = 1
        self.adjacents = self.check_adjacents()
        for i in self.adjacents:
            base[i] = 1
        safe_cells, monster, precipices, exit = self.agent.process_percept(
            base, self.pos, self.visited, self.at_exit, self.at_monster
        )
        known = [safe_cells, monster, precipices, exit]
        self.check_predictions(known)
        self.safe_cells.extend(safe_cells + exit)
        self.viewed.extend(safe_cells + monster + precipices + exit)
        return base

    def check_adjacents(self):
        """
        Checks the content of the adjacent cells to the current one

        Returns:
            list: the contents of those cells
        """
        adj = []
        if self.pos[1] > 0:
            left = self.percepts_translation.get(
                self.state[self.pos[0]][self.pos[1] - 1], None
            )
        else:
            left = None
        if self.pos[1] < self.size - 1:
            right = self.percepts_translation.get(
                self.state[self.pos[0]][self.pos[1] + 1], None
            )
        else:
            right = None

        if self.pos[0] > 0:
            up = self.percepts_translation.get(
                self.state[self.pos[0] - 1][self.pos[1]], None
            )
        else:
            up = None
        if self.pos[0] < self.size - 1:
            down = self.percepts_translation.get(
                self.state[self.pos[0] + 1][self.pos[1]], None
            )
        else:
            down = None
        for i in [left, right, up, down]:
            if i is not None:
                adj.append(i)
        return adj

    def check_predictions(self, predictions):
        """
        Verification of the logical model's predictions

        Args:
            predictions (list): list with lists for each type of prediction
        """
        if self.playing:
            pred_dict = {0: "    ", 1: "M   ", 2: "P   ", 3: "S   "}
            try:
                for ind, category in enumerate(predictions):
                    for prediction in category:
                        symbol = pred_dict[ind]
                        if self.state[prediction[0]][prediction[1]] != "CK  ":
                            assert symbol == self.state[prediction[0]][prediction[1]]
            except AssertionError as e:
                print("The logical model made an incorrect prediction")

    def execute_action(self, action):
        """
        Executes a given action

        Args:
            action (str): the action
        """
        pos_before = self.pos.copy()
        if action == "LEFT":
            if self.percept[5] != 1:
                self.pos[1] -= 1
            else:
                print("You can't move left, there's a wall")
        elif action == "RIGHT":
            if self.percept[6] != 1:
                self.pos[1] += 1
            else:
                print("You can't move right, there's a wall")
        elif action == "UP":
            if self.percept[3] != 1:
                self.pos[0] -= 1
            else:
                print("You can't move up, there's a wall")
        elif action == "DOWN":
            if self.percept[4] != 1:
                self.pos[0] += 1
            else:
                print("You can't move down, there's a wall")
        elif action == "GRENADE":
            if self.grenade:
                self.grenade = False
                if self.percept[1] == 1:
                    self.scream = True
                    self.monster_dead = True

            else:
                print("You have no grenades left")

        elif action == "EXIT":
            if self.at_exit:
                if self.kurt_found:
                    print("Congratulations, you have escaped the maze")
                else:
                    print("You escape the maze, but leave Kurt behind")
                self.playing = False
            else:
                print("You are not at the exit")
        if pos_before != self.pos:
            if self.at_exit:
                self.state[pos_before[0]][pos_before[1]] = "S   "
                self.at_exit = False
            elif self.at_monster:
                self.state[pos_before[0]][pos_before[1]] = "M   "
                self.at_monster = False
            else:
                self.state[pos_before[0]][pos_before[1]] = "    "
            self.check_after_move()
            self.state[self.pos[0]][self.pos[1]] = self.Wilson_characters

    def check_after_move(self):
        """
        Checks what should happen after the player's move
        """
        cell_content = self.percepts_translation.get(
            self.state[self.pos[0]][self.pos[1]], None
        )
        if cell_content in [0, 1]:
            if not self.monster_dead:
                self.playing = False
            if cell_content == 0:
                print("You fell into a precipice. Mission failed")
            elif not self.monster_dead:
                print("The monster ate you. Mission failed")
            else:
                self.at_monster = True
                print("You see the monster's corpse")
        elif cell_content == 2:
            self.at_exit = True
            if self.search:
                self.search.exit_pos = self.pos.copy()
            print("You are at the exit")
        elif self.state[self.pos[0]][self.pos[1]] == "CK  ":
            self.kurt_found = True
            if self.search:
                self.search.kurt_found = True
            self.Wilson_characters = "CWCK"

        if self.pos not in self.visited:
            self.visited.append(self.pos.copy())
        self.percept = self.generate_percept()

    def run_maze(self):
        """
        Runs the maze
        """
        print("Welcome to the maze")
        print(
            "The available actions are: W (up), S (down), A (left), D (right), E (exit) and G (grenade)"
        )
        while self.playing:
            print(str(self))

            if not self.search:
                action = self.request_action()
            else:
                action = self.search.give_next_move(
                    self.safe_cells, self.pos, self.visited
                )
            self.execute_action(action)


class BayesianMaze(BaseMaze):
    """
    Class that runs the Bayesian maze
    """

    def __init__(self, n=6, sol=False, auto=False) -> None:
        """
        Class constructor

        Args:
            n (int, optional): size of the maze. Defaults to 6.
            sol (bool, optional): whether to show it solved. Defaults to False.
            auto (bool, optional): whether to use the search algorithm. Defaults to False.
        """
        super().__init__(n, sol)
        self.state = self.generate_initial_state()
        self.search = None
        if auto:
            self.search = BayesianSearch(n)
        self.dart = True
        self.frontier = [(0, 1), (1, 0)]
        self.agent = BayesianAgent(n)

        self.percepts_translation = {"F": 0, "P": 1, "D": 2, "M": 3, "S": 4}
        self.messages = {
            0: "You smell kerosene",
            1: "The ground creaks",
            2: "You see wires",
            3: "You smell something",
            4: "You see a light",
            5: "You hear a scream",
        }
        self.input_to_actions = {
            "W": "UP",
            "S": "DOWN",
            "A": "LEFT",
            "D": "RIGHT",
            "B": "BLOWGUN",
            "E": "EXIT",
        }

        self.percept = self.generate_percept()
        self.playing = True
        self.run_maze()

    def generate_initial_state(self):
        """
        Generates the initial state. Traps can share a cell, as can CK, M, and S, but
        they cannot mix. The start remains free

        Returns:
            list: matrix representing the maze
        """
        base = [["    " for _ in range(self.size)] for _ in range(self.size)]
        base[0][0] = self.Wilson_characters
        for i in ["F   ", "P   ", "D   "]:
            x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            while [x, y] == [0, 0]:
                x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            if base[x][y] != "    ":
                merged = base[x][y].strip() + i.strip()
                base[x][y] = merged + " " * (4 - len(merged))
            else:
                base[x][y] = i
        for i in ["M   ", "CK  ", "S   "]:
            x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            while base[x][y] in ["F   ", "P   ", "D   "] or [x, y] == [0, 0]:
                x, y = [random.randint(0, self.size - 1) for _ in range(2)]
            if base[x][y] != "    ":
                merged = base[x][y].strip() + i.strip()
                base[x][y] = merged + " " * (4 - len(merged))
            else:
                base[x][y] = i
        return base

    def generate_percept(self):
        """
        Generates a percept based on the player's position. This percept is processed
        by the Bayesian agent, which returns its prediction.

        Returns:
            list: list with percept information (order of slides plus Kurtz at the end)
        """
        base = [0 for _ in range(11)]
        if self.pos[1] == 0:
            base[7] = 1
        elif self.pos[1] == self.size - 1:
            base[8] = 1
        if self.pos[0] == 0:
            base[5] = 1
        elif self.pos[0] == self.size - 1:
            base[6] = 1
        if self.scream:
            base[9] = 1
        if self.kurt_found:
            base[10] = 1
        self.adjacents = self.check_adjacent()
        for l in self.state[self.pos[0]][self.pos[1]]:
            if l != " ":
                val = self.percepts_translation.get(l, None)
                if val is not None:
                    base[val] = 1
        for i in self.adjacents:
            base[i] = 1
        self.agent.process_percepts(base, self.pos)

        return base

    def choose_best_cell(self, probability_matrix):
        """
        Greedy algorithm to choose the next move. Given the
        probability matrix, it chooses the cell in the frontier with the least
        chance of the player dying

        Args:
            probability_matrix (list): matrix with the probabilities of elements for each cell

        Returns:
            tuple: the node we want to go to
        """
        prob_die = lambda x: sum(
            i for i in x[:4]
        )  # sum of the 4 probabilities because they are disjoint
        next_move = min(
            self.frontier, key=lambda x: prob_die(probability_matrix[x[0]][x[1]])
        )
        return next_move

    def check_adjacent(self):
        """
        Checks the content of the cells adjacent to the current one

        Returns:
            list: the contents of those cells
        """
        adj = []
        if self.pos[1] > 0:
            for l in self.state[self.pos[0]][self.pos[1] - 1]:
                v = self.percepts_translation.get(l, None)
                if v is not None:
                    adj.append(v)

        if self.pos[1] < self.size - 1:
            for l in self.state[self.pos[0]][self.pos[1] + 1]:
                v = self.percepts_translation.get(l, None)
                if v is not None:
                    adj.append(v)

        if self.pos[0] > 0:
            for l in self.state[self.pos[0] - 1][self.pos[1]]:
                v = self.percepts_translation.get(l, None)
                if v is not None:
                    adj.append(v)

        if self.pos[0] < self.size - 1:
            for l in self.state[self.pos[0] + 1][self.pos[1]]:
                v = self.percepts_translation.get(l, None)
                if v is not None:
                    adj.append(v)

        return adj

    def execute_action(self, action):
        """
        Executes a given action

        Args:
            action (str): the action
        """
        pos_before = self.pos.copy()
        if action == "LEFT":
            if self.percept[7] != 1:
                self.pos[1] -= 1
            else:
                print("You can't move left, there's a wall")
        elif action == "RIGHT":
            if self.percept[8] != 1:
                self.pos[1] += 1
            else:
                print("You can't move right, there's a wall")
        elif action == "UP":
            if self.percept[5] != 1:
                self.pos[0] -= 1
            else:
                print("You can't move up, there's a wall")
        elif action == "DOWN":
            if self.percept[6] != 1:
                self.pos[0] += 1
            else:
                print("You can't move down, there's a wall")

        elif action == "BLOWGUN":
            if self.dart:
                a = b = -1
                while a not in range(0, self.size) and b not in range(0, self.size):
                    if a != -1 or b != -1:
                        print("The dart hits the wall, choose another direction")
                    direction = input(
                        "Choose the direction of the dart, W (up), S (down), A (left) or D (right): "
                    )
                    while direction.lower() not in ["w", "a", "s", "d"]:
                        direction = input(
                            "Choose the direction of the dart, W (up), S (down), A (left) or D (right): "
                        )
                    if direction == "w":
                        a = self.pos[0] - 1
                        b = self.pos[1]
                    elif direction == "s":
                        a = self.pos[0] + 1
                        b = self.pos[1]
                    elif direction == "a":
                        a = self.pos[0]
                        b = self.pos[1] - 1
                    else:
                        a = self.pos[0]
                        b = self.pos[1] + 1
                if "M" in self.state[a][b]:
                    self.scream = True
                    self.monster_dead = True

                self.dart = False
            else:
                print("You have no darts left")
        elif action == "EXIT":
            if self.at_exit:
                if self.kurt_found:
                    print("Congratulations, you have escaped the maze")
                else:
                    print("You escape the maze, but leave Kurt behind")
                self.playing = False
            else:
                print("You are not at the exit")
        if pos_before != self.pos:
            text = ""

            if self.at_exit:
                text += "S"
                self.at_exit = False
            if self.at_monster:
                text += "M"
                self.at_monster = False
            self.state[pos_before[0]][pos_before[1]] = text + " " * (4 - len(text))
            if self.pos not in self.visited:
                self.frontier.remove(tuple(self.pos))
            self.check_after_move()
            self.state[self.pos[0]][self.pos[1]] = self.Wilson_characters

    def get_adjacent(self, row, col, visited):
        """
        Given a row and column, returns the adjacent cells that have not
        been visited

        Args:
            row (int): row
            col (int): column
            visited (list): already visited cells

        Returns:
            list: unvisited adjacent cells
        """
        adjacent = []
        for x, y in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
            if (
                x in range(0, self.size)
                and y in range(0, self.size)
                and [x, y] not in visited
            ):
                adjacent.append((x, y))

        return adjacent

    def check_after_move(self):
        """
        Checks what should happen after the player's move
        """
        cell_list = []
        for l in self.state[self.pos[0]][self.pos[1]]:
            if l != " ":
                cell_list.append(self.percepts_translation.get(l, None))
        for cell_content in cell_list:
            if cell_content in [0, 1, 2, 3]:
                if not self.monster_dead:
                    self.playing = False
                if cell_content == 0:
                    print("You burned in the fire trap. Mission failed")
                elif cell_content == 1:
                    print("You fell into the spike trap. Mission failed")
                elif cell_content == 2:
                    print("You fell into the dart trap. Mission failed")
                elif not self.monster_dead:
                    print("The monster ate you. Mission failed")
                else:
                    self.at_monster = True
                    print("You see the monster's corpse")
            elif cell_content == 4:
                self.at_exit = True
                if self.search:
                    self.search.exit_pos = self.pos.copy()
                print("You are at the exit")
            elif self.state[self.pos[0]][self.pos[1]] == "CK  ":
                self.kurt_found = True
                if self.search:
                    self.search.kurt_found = True
                self.Wilson_characters = "CWCK"

        if self.pos not in self.visited:
            self.visited.append(self.pos.copy())
        for i in self.get_adjacent(self.pos[0], self.pos[1], self.visited):
            if i not in self.frontier + self.pos:
                self.frontier.append(i)
        self.percept = self.generate_percept()

    def run_maze(self):
        """
        Runs the maze
        """
        print("Welcome to the maze")
        print(
            "The available actions are: W (up), S (down), A (left), D (right), E (exit) and B (blowdart)"
        )
        while self.playing:
            print(str(self))
            cell = self.choose_best_cell(self.agent.probability_matrix)

            print(f"The best cell to move to is: ({cell[0]+1}, {cell[1]+1})")
            if not self.search:
                action = self.request_action()
            else:
                action = self.search.give_next_move(
                    self.agent.probability_matrix,
                    self.pos,
                    self.visited,
                )
                time.sleep(0.05)
            self.execute_action(action)
