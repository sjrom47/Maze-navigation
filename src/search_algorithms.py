class SearchAlgorithms:
    """
    Base class that contains various search algorithms and support functions
    """

    def __init__(self, n) -> None:
        """
        Class constructor

        Args:
            n (int): the size of the maze
        """
        self.n = n
        self.frontier = []
        self.generated_moves = []

    def choose_bfs_move(self, safe_cells):
        """
        Chooses the next move using the BFS algorithm. It first picks from
        the safe cells and then from the rest

        Args:
            safe_cells (list): safe cells

        Returns:
            tuple: the destination cell
        """
        safe_list = [(x, y) for x, y in self.frontier if [x, y] in safe_cells]
        if safe_list:
            next_move = safe_list[0]
        else:
            next_move = self.frontier[0]
        return next_move

    def a_star_on_known(self, start, goal, visited):
        """
        Finds the shortest path from one visited cell to another using
        the A* algorithm

        Args:
            start (tuple): starting cell
            goal (tuple): goal cell
            visited (list): cells we can move through

        Returns:
            list: path to the goal
        """
        f_score = lambda x: abs(x[0] - goal[0]) + abs(x[1] - goal[1])
        values = {start: f_score(start)}

        parents = {}
        costs = {start: 0}

        while values:
            current_node = min(values, key=lambda x: values[x])

            del values[current_node]

            if (
                goal in self.get_adjacent(current_node[0], current_node[1], visited)
                or goal == current_node
            ):
                path = []
                while current_node in parents:
                    path.append(current_node)
                    current_node = parents[current_node]

                return path[::-1]
            visited_adj = self.get_visited_adjacent(
                current_node[0], current_node[1], visited
            )
            for neighbor in visited_adj:
                hypothetical_value = costs[current_node] + 1 + f_score(neighbor)
                if tuple(neighbor) not in costs or hypothetical_value < values.get(
                    tuple(neighbor), -1
                ):
                    values[tuple(neighbor)] = hypothetical_value
                    costs[tuple(neighbor)] = costs[tuple(current_node)] + 1
                    parents[tuple(neighbor)] = current_node

        return None

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
                x in range(0, self.n)
                and y in range(0, self.n)
                and [x, y] not in visited
            ):
                adjacent.append((x, y))

        return adjacent

    def get_visited_adjacent(self, row, col, visited):
        """
        Given a row and column, gets the adjacent cells that have been visited

        Args:
            row (int): row
            col (int): column
            visited (list): visited cells

        Returns:
            list: visited adjacent cells
        """
        visited_adjacent = []
        for x, y in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
            if (
                x in range(0, self.n)
                and y in range(0, self.n)
                and [x, y] in visited
                and [x, y] != [row, col]
            ):
                visited_adjacent.append([x, y])
        return visited_adjacent

    def convert_to_actions(self, node_list, pos):
        """
        Given a list of nodes, gets the corresponding actions to move
        through those nodes in that order

        Args:
            node_list (list): list of nodes to move through
            pos (tuple): initial position

        Returns:
            list: list of actions
        """
        diff = lambda x, y: (y[0] - x[0], y[1] - x[1])
        actions = {
            (1, 0): "UP",
            (-1, 0): "DOWN",
            (0, 1): "LEFT",
            (0, -1): "RIGHT",
            (0, 0): "EXIT",
        }
        action_list = []
        current_node = pos
        for node in node_list:
            action_list.append(actions[diff(node, current_node)])
            current_node = node
        return action_list

    def choose_greedy_move(self, probability_matrix):
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


class LogicalSearch(SearchAlgorithms):
    """
    Search in the logical maze
    """

    def __init__(self, n=6) -> None:
        """
        Class constructor

        Args:
            n (int, optional): size of the maze. Defaults to 6.
        """
        super().__init__(n)
        self.kurt_found = False
        self.exit_pos = []
        self.previous_goal = None

    def give_next_move(self, safe_cells, pos, visited):
        """
        Gets the next move. If there are generated moves, it returns
        the next one, otherwise it generates the next moves

        Args:
            safe_cells (list): safe cells
            pos (list): player's position
            visited (list): visited cells

        Returns:
            str: the action to be executed
        """
        for i in self.get_adjacent(pos[0], pos[1], visited):
            if i not in self.frontier + pos:
                self.frontier.append(i)
        if (
            self.kurt_found and self.exit_pos and not self.generated_moves
        ):  # if we have found Kurtz and the exit, we go directly to the exit and leave the maze
            if self.exit_pos != pos:
                path = self.a_star_on_known(tuple(pos), tuple(self.exit_pos), visited)
            else:
                path = [tuple(self.exit_pos)]
            self.generated_moves = self.convert_to_actions(path, pos) + ["EXIT"]

        elif not self.generated_moves:  # Generate new moves
            if self.previous_goal:
                self.frontier.remove(tuple(self.previous_goal))
            path = []
            final_goal = self.choose_bfs_move(safe_cells)
            if final_goal not in self.get_adjacent(pos[0], pos[1], visited):
                path = self.a_star_on_known(tuple(pos), tuple(final_goal), visited)

            self.generated_moves = self.convert_to_actions(path + [final_goal], pos)
            self.previous_goal = final_goal
        move = self.generated_moves.pop(0)
        print(move)
        return move


class BayesianSearch(SearchAlgorithms):
    """
    Bayesian search class
    """

    def __init__(self, n=6) -> None:
        """
        Class constructor

        Args:
            n (int, optional): The size of the maze. Defaults to 6.
        """
        super().__init__(n)
        self.kurt_found = False
        self.exit_pos = []
        self.previous_goal = None

    def give_next_move(self, probability_matrix, pos, visited):
        """
        Gets the next move. If there are generated moves, it returns
        the next one, otherwise it generates the next moves

        Args:
            probability_matrix (list): matrix with the probabilities of the presence of each element
            pos (list): player's position
            visited (list): visited cells

        Returns:
            str: next action
        """
        for i in self.get_adjacent(pos[0], pos[1], visited):
            if i not in self.frontier + pos:
                self.frontier.append(i)
        if self.kurt_found and self.exit_pos and not self.generated_moves:
            if self.exit_pos != pos:
                path = self.a_star_on_known(tuple(pos), tuple(self.exit_pos), visited)
            else:
                path = [tuple(self.exit_pos)]
            self.generated_moves = self.convert_to_actions(path, pos) + ["EXIT"]

        elif not self.generated_moves:
            if self.previous_goal:
                self.frontier.remove(tuple(self.previous_goal))
            path = []
            final_goal = self.choose_greedy_move(probability_matrix)
            if final_goal not in self.get_adjacent(pos[0], pos[1], visited):
                path = self.a_star_on_known(tuple(pos), tuple(final_goal), visited)

            self.generated_moves = self.convert_to_actions(path + [final_goal], pos)
            self.previous_goal = final_goal
        move = self.generated_moves.pop(0)
        print(move)
        return move
