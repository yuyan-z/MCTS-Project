from board import get_possible_cors


class HumanPlayer:
    def __init__(self, name, corner_cors, win_threshold):
        self.selected_piece = None
        self.role = "human"
        self.name = name
        self.corner_cors = corner_cors
        self.win_threshold = win_threshold

    def reset_selected_piece(self):
        self.selected_piece = None

    def move(self, clicked_cor, grid):
        res = (self.selected_piece, None)

        if clicked_cor:
            # Set selected_piece
            if self.selected_piece is None:
                if grid[clicked_cor]['piece'] == self.name:
                    self.selected_piece = clicked_cor
                    res = (clicked_cor, None)
            # Reset selected_piece
            elif self.selected_piece == clicked_cor:
                self.selected_piece = None
                res = (None, None)
            # Move
            elif self.check_move(clicked_cor, grid):
                res = (self.selected_piece, clicked_cor)

        return res

    def check_move(self, clicked_cor, grid):
        can_move = False
        if self.selected_piece is not None and self.selected_piece != clicked_cor:
            cors = get_possible_cors(self.selected_piece, grid)
            if clicked_cor in cors:
                can_move = True

        return can_move

    def get_pieces(self, grid):
        return [cor for cor, cell in grid.items() if cell['piece'] == self.name]

    def check_win(self, grid):
        pieces = self.get_pieces(grid)
        count = sum(1 for piece in pieces if piece in self.corner_cors)
        return count >= self.win_threshold

    def get_n_pieces_corner(self, grid):
        pieces = self.get_pieces(grid)
        return sum(1 for p in pieces if p in self.corner_cors)
