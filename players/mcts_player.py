import math
import random
from board import get_possible_cors

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.untried_moves = None

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
        return max(
            self.children,
            key=lambda child: (child.total_reward / child.visits if child.visits > 0 else 0)
                               + c_param * math.sqrt(math.log(self.visits + 1) / (child.visits + 1))
        )


class MCTSPlayer:
    def __init__(self, name, corner_cors, simulations=100, c=1.4):
        self.role = "mcts"
        self.name = name
        self.corner_cors = corner_cors
        self.simulations = simulations
        self.c = c

    def get_pieces(self, grid):
        return [cor for cor, cell in grid.items() if cell['piece'] == self.name]

    def move(self, grid):
        root = MCTSNode(state=self.deepcopy_grid(grid))

        for _ in range(self.simulations):
            node = self.tree_policy(root)
            reward = self.default_policy(node.state)
            self.backup(node, reward)

        best_child = root.best_child(c_param=0)
        print("MCTS selected move:", best_child.move)
        return best_child.move

    def tree_policy(self, node):
        while not self.is_terminal(node.state):
            if not node.is_fully_expanded(self.name):
                return self.expand(node)
            else:
                node = node.best_child(self.c)
        return node

    def expand(self, node):
        if node.untried_moves is None:
            node.untried_moves = node.get_all_moves(self.name)

        tried_moves = [child.move for child in node.children]
        untried = [move for move in node.untried_moves if move not in tried_moves]

        if not untried:
            return random.choice(node.children)

        move = random.choice(untried)
        new_state = self.simulate_move(node.state, move)
        child_node = MCTSNode(state=new_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def default_policy(self, state):
        # Minimize the average distance between chess pieces and the target angle
        total_distance = 0
        pieces = [cor for cor, cell in state.items() if cell['piece'] == self.name]
        for piece in pieces:
            min_dist = min(self.hex_distance(piece, target) for target in self.corner_cors)
            total_distance += min_dist
        if not pieces:
            return 0
        avg_distance = total_distance / len(pieces)
        return 1 / (avg_distance + 1e-6)

    def backup(self, node, reward):
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            node = node.parent

    def simulate_move(self, state, move):
        new_state = self.deepcopy_grid(state)
        from_cor, to_cor = move
        new_state[to_cor]['piece'] = new_state[from_cor]['piece']
        new_state[from_cor]['piece'] = None
        return new_state

    def is_terminal(self, state):
        pieces = self.get_pieces(state)
        return all(cor in self.corner_cors for cor in pieces)

    def hex_distance(self, a, b):
        aq, ar = a
        bq, br = b
        return (abs(aq - bq) + abs(ar - br) + abs((aq + ar) - (bq + br))) // 2

    def deepcopy_grid(self, grid):
        return {cor: cell.copy() for cor, cell in grid.items()}

    def get_n_pieces_corner(self, grid):
        pieces = self.get_pieces(grid)
        return sum(1 for p in pieces if p in self.corner_cors)
