import pandas as pd
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
NAME1 = "GRAVE"
NAME2 = "MCTS"
WIN_THRESHOLD = 6 # 1-10
MAX_MOVE_COUNT = 200
C = 1.4

# TIME_DELAY = 100
TIME_DELAY = 0

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

        if ai.get_n_pieces_corner(GRID) >= WIN_THRESHOLD:
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

    # PLAYER1 = RandomPlayer(NAME1, corner_cors2)
    # PLAYER1 = MCTSPlayer(NAME1, corner_cors2, simulations=300)
    PLAYER1 = GRAVEPlayer(NAME1, corner_cors2, simulations=300, c=C)
    # PLAYER2 = HumanPlayer(NAME2, corner_cors1)
    # PLAYER2 = RandomPlayer(NAME2, corner_cors1)
    PLAYER2 = MCTSPlayer(NAME2, corner_cors1, simulations=300, c=C)
    player = PLAYER2
    selected_piece = None
    winner = None
    isEnd = False

    count = 0
    while not isEnd:
        clock.tick(30)
        draw_board(screen, GRID, selected_piece)

        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Move Count: {count}", True, (0, 0, 0))
        screen.blit(text, (10, 10))

        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Player 1: {PLAYER1.role}", True, (0, 0, 0))
        screen.blit(text, (10, 50))
        text = font.render(f"Player 2: {PLAYER2.role}", True, (0, 0, 0))
        screen.blit(text, (10, WINDOW_HEIGHT - 50))

        pygame.display.flip()

        new_turn = None
        if player.role != "human":
            pygame.time.delay(TIME_DELAY)
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
        elif new_turn == "win":
            winner = player.name
            isEnd = True
        else:
            player = new_turn
            count += 1

            if count >= MAX_MOVE_COUNT:
                print("Too many moves.")
                isEnd = True
                if PLAYER1.get_n_pieces_corner(GRID) > PLAYER2.get_n_pieces_corner(GRID):
                    winner = NAME1
                elif PLAYER2.get_n_pieces_corner(GRID) > PLAYER1.get_n_pieces_corner(GRID):
                    winner = NAME2

        if winner:
            print(f"{winner} Win")
            font = pygame.font.SysFont(None, 36)
            text = font.render(f"{winner} Win", True, (0, 0, 0))
            screen.blit(text, (WINDOW_WIDTH // 2 - 50, 10))
            pygame.display.flip()
    pygame.time.delay(TIME_DELAY*10)
    return winner


if __name__ == '__main__':
    win_counts = {NAME1: 0, NAME2: 0}
    n = 300

    for _ in range(n):
        winner = main()
        if winner:
            win_counts[winner] += 1

    win_rates = {
        NAME1: win_counts[NAME1] / n,
        NAME2: win_counts[NAME2] / n
    }
    print(win_rates)

    df = pd.DataFrame({
        "Agent": [NAME1, NAME2],
        "Win Rate": [win_rates[NAME1], win_rates[NAME2]],
        "Win Count": [win_counts[NAME1], win_counts[NAME2]]
    })
    df.to_csv(f"win_rates_{NAME1}_{NAME2}_{C}.csv", index=False)




