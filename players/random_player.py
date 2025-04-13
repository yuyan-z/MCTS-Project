import random

from board import get_possible_cors


class RandomPlayer:
    def __init__(self, name, corner_cors, win_threshold):
        self.role = "random"
        self.name = name
        self.corner_cors = corner_cors
        self.win_threshold = win_threshold

    def get_pieces(self, grid):
        return [cor for cor, cell in grid.items() if cell['piece'] == self.name]

    def move(self, grid):
        pieces = self.get_pieces(grid)
        moves = []
        for piece in pieces:
            cors = get_possible_cors(piece, grid)
            moves_piece = [(piece, cor) for cor in cors]
            moves.extend(moves_piece)

        print("Ramdom moves:", moves)
        return random.choice(moves)

    def check_win(self, grid):
        pieces = self.get_pieces(grid)
        count = sum(1 for piece in pieces if piece in self.corner_cors)
        return count >= self.win_threshold


