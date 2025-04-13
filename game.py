import pygame
import sys
import math

from board import WINDOW_WIDTH, WINDOW_HEIGHT, init_gird, draw_board, get_cor_at_pos
from human_player import HumanPlayer
from players.grave_player import GRAVEPlayer
from players.mcts_player import MCTSPlayer
from players.random_player import RandomPlayer

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chinese Checker - 2 Players")

GRID = {}  # {(q, r): {'pos': (x, y), 'piece': name1/name2/None}}
PLAYER1 = None
PLAYER2 = None
NAME1 = "ai"
NAME2 = "ai2"
WIN_THRESHOLD = 5  # 0-10


def switch_player(player):
    global PLAYER1, PLAYER2
    return PLAYER2 if player.name == PLAYER1.name else PLAYER1


def ai_move(ai):
    print(f"-- {ai.name} move --")
    turn = None
    piece, cor = ai.move(GRID)
    if piece and cor:
        GRID[cor]['piece'] = GRID[piece]['piece']
        GRID[piece]['piece'] = None

        if ai.check_win(GRID):
            turn = "win"
        else:
            turn = switch_player(ai)

    return turn


def human_move(human, clicked_cor):
    print(f"-- {human.name} move --")
    turn = None
    piece, cor = human.move(clicked_cor, GRID)
    if piece and cor:
        GRID[cor]['piece'] = GRID[piece]['piece']
        GRID[piece]['piece'] = None
        human.reset_selected_piece()
        piece = None

        if human.check_win(GRID):
            turn = "win"
        else:
            print("here")
            turn = switch_player(human)

    return turn, piece


def main():
    clock = pygame.time.Clock()

    global GRID, NAME1, NAME2, PLAYER1, PLAYER2
    GRID, corner_cors1, corner_cors2 = init_gird(NAME1, NAME2)
    print("GRID: ", GRID)

    # PLAYER1 = RandomPlayer(NAME1, corner_cors2, WIN_THRESHOLD)
    # PLAYER1 = MCTSPlayer(NAME1, corner_cors2, WIN_THRESHOLD)
    PLAYER1 = GRAVEPlayer(NAME1, corner_cors2, WIN_THRESHOLD)
    # PLAYER2 = HumanPlayer(NAME2, corner_cors1, WIN_THRESHOLD)
    PLAYER2 = RandomPlayer(NAME2, corner_cors1, WIN_THRESHOLD)
    player = PLAYER2
    selected_piece = None

    while True:
        clock.tick(30)
        draw_board(screen, GRID, selected_piece)
        pygame.display.flip()

        new_turn = None
        if player.role != "human":
            pygame.time.delay(500)
            new_turn = ai_move(player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and player.role == "human":
                mouse_pos = pygame.mouse.get_pos()
                clicked_cor = get_cor_at_pos(mouse_pos, GRID)
                new_turn, selected_piece = human_move(player, clicked_cor)

        if new_turn is None:
            pass
        elif new_turn== "win":
            print(f"{player.name} win")
            break
        else:
            player = new_turn


if __name__ == '__main__':
    main()
