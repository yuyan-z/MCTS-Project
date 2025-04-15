import math
import random
from board import get_possible_cors


class GRAVENode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.untried_moves = None

        # GRAVE
        self.amaf_visits = {}  # move -> int
        self.amaf_total_reward = {}    # move -> float

    def get_all_moves(self, player_name):
        pieces = [cor for cor, cell in self.state.items() if cell['piece'] == player_name]
        moves = []
        for piece in pieces:
            for to in get_possible_cors(piece, self.state):
                moves.append((piece, to))
        return moves

    def is_fully_expanded(self, player_name):
        if self.untried_moves is None:
            self.untried_moves = self.get_all_moves(player_name)
        tried_moves = [child.move for child in self.children]
        return len(tried_moves) >= len(self.untried_moves)

    def best_child(self, c_param=1.4):
        def grave_score(child):
            move = child.move
            q = child.total_reward / child.visits if child.visits > 0 else 0
            amaf_v = self.amaf_visits.get(move, 0)
            amaf_w = self.amaf_total_reward.get(move, 0)
            q_amaf = amaf_w / amaf_v if amaf_v > 0 else 0

            beta = child.visits / (child.visits + amaf_v + 1e-6)
            grave_q = beta * q + (1 - beta) * q_amaf

            return grave_q + c_param * math.sqrt(math.log(self.visits + 1) / (child.visits + 1))

        return max(self.children, key=grave_score)


class GRAVEPlayer:
    def __init__(self, name, corner_cors, simulations=100, c=1.4):
        self.role = "grave"
        self.name = name
        self.corner_cors = corner_cors
        self.simulations = simulations
        self.c = c

    def get_pieces(self, grid):
        return [cor for cor, cell in grid.items() if cell['piece'] == self.name]

    def move(self, grid):
        root = GRAVENode(state=self.deepcopy_grid(grid))

        for _ in range(self.simulations):
            node, path, played_moves = self.tree_policy(root)
            reward = self.default_policy(node.state)
            self.backup(path, played_moves, reward)

        best_child = root.best_child(c_param=0)
        print("GRAVE selected move:", best_child.move)
        return best_child.move

    def tree_policy(self, node):
        path = []
        played_moves = set()

        while not self.is_terminal(node.state):
            path.append(node)
            if not node.is_fully_expanded(self.name):
                new_node = self.expand(node)
                path.append(new_node)
                played_moves.add(new_node.move)
                return new_node, path, played_moves
            else:
                node = node.best_child(self.c)
                played_moves.add(node.move)

        return node, path, played_moves

    def expand(self, node):
        if node.untried_moves is None:
            node.untried_moves = node.get_all_moves(self.name)

        tried_moves = [child.move for child in node.children]
        untried = [move for move in node.untried_moves if move not in tried_moves]

        if not untried:
            return random.choice(node.children)

        move = random.choice(untried)
        new_state = self.simulate_move(node.state, move)
        child = GRAVENode(state=new_state, parent=node, move=move)
        node.children.append(child)
        return child

    def default_policy(self, state):
        # Minimize the average distance between chess pieces and the target angle
        pieces = [cor for cor, cell in state.items() if cell['piece'] == self.name]
        if not pieces:
            return 0
        total = 0
        for piece in pieces:
            min_dist = min(self.hex_distance(piece, goal) for goal in self.corner_cors)
            total += min_dist
        return 1 / (1 + total / len(pieces))

    def backup(self, path, played_moves, reward):
        for node in reversed(path):
            node.visits += 1
            node.total_reward += reward
            for move in played_moves:
                node.amaf_visits[move] = node.amaf_visits.get(move, 0) + 1
                node.amaf_total_reward[move] = node.amaf_total_reward.get(move, 0) + reward

    def simulate_move(self, grid, move):
        new_grid = self.deepcopy_grid(grid)
        from_cor, to_cor = move
        new_grid[to_cor]['piece'] = new_grid[from_cor]['piece']
        new_grid[from_cor]['piece'] = None
        return new_grid

    def is_terminal(self, state):
        pieces = self.get_pieces(state)
        return all(cor in self.corner_cors for cor in pieces)

    def deepcopy_grid(self, grid):
        return {cor: cell.copy() for cor, cell in grid.items()}

    def hex_distance(self, a, b):
        aq, ar = a
        bq, br = b
        return (abs(aq - bq) + abs(ar - br) + abs((aq + ar) - (bq + br))) // 2

    def get_n_pieces_corner(self, grid):
        pieces = self.get_pieces(grid)
        return sum(1 for p in pieces if p in self.corner_cors)