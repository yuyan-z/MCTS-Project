import pygame
import math

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

CELL_RADIUS = 20
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
OFFSET_X = WINDOW_WIDTH // 2
OFFSET_Y = WINDOW_HEIGHT // 2

PIECES_HEIGHTS = 4  # 0.5*(k+1)(k) = 10
# PIECES_HEIGHTS = 3  # 0.5*(k+1)(k) = 6

NAME1 = None
# BOARD_SIZE = 8
BOARD_SIZE = 6


def hex_to_pixel(r, q):
    x = OFFSET_X + CELL_RADIUS * math.sqrt(3) * (q + r / 2)
    y = OFFSET_Y + CELL_RADIUS * 1.5 * r
    return (int(x), int(y))


def init_gird(name1, name2):
    global NAME1
    NAME1 = name1
    HALF_BOARD_SIZE = BOARD_SIZE // 2

    grid = {}
    corner_cors1 = []
    corner_cors2 = []

    for r in range(-BOARD_SIZE, BOARD_SIZE+1):
        q_min = max(-HALF_BOARD_SIZE, -r - HALF_BOARD_SIZE)
        q_max = min(HALF_BOARD_SIZE, -r + HALF_BOARD_SIZE)
        for q in range(q_min, q_max + 1):
            pos = hex_to_pixel(r, q)
            grid[(r, q)] = {'pos': pos, 'piece': None}

            # pieces in top side
            if r < -HALF_BOARD_SIZE + (PIECES_HEIGHTS - HALF_BOARD_SIZE):
                corner_cors1.append((r, q))
                grid[(r, q)]['piece'] = name1
            # pieces in bottom side
            if r > HALF_BOARD_SIZE - (PIECES_HEIGHTS - HALF_BOARD_SIZE):
                corner_cors2.append((r, q))
                grid[(r, q)]['piece'] = name2

    return grid, corner_cors1, corner_cors2


def draw_board(screen, gird, selected_piece=None):
    screen.fill(WHITE)
    font = pygame.font.SysFont(None, 16)
    for (r, q), cell in gird.items():
        x, y = cell['pos']
        pygame.draw.circle(screen, GRAY, (x, y), CELL_RADIUS - 3, 1)
        if cell['piece']:
            color = RED if cell['piece'] == NAME1 else BLUE
            pygame.draw.circle(screen, color, (x, y), CELL_RADIUS - 3)

        if selected_piece == (r, q):
            pygame.draw.circle(screen, BLACK, (x, y), CELL_RADIUS - 3, 2)

        label = font.render(f"{r},{q}", True, BLACK)
        label_rect = label.get_rect(center=(x, y))
        screen.blit(label, label_rect)


def get_cor_at_pos(pos, grid):
    cor = None
    for (r, q), cell in grid.items():
        x, y = cell['pos']
        distance = math.hypot(pos[0] - x, pos[1] - y)
        if distance <= CELL_RADIUS:
            cor = (r, q)
    return cor


def get_cors_by_distance(cors, distance):
    return [
        (cors[0], cors[1] - distance),
        (cors[0], cors[1] + distance),
        (cors[0] - distance, cors[1]),
        (cors[0] + distance, cors[1]),
        (cors[0] + distance, cors[1] - distance),
        (cors[0] - distance, cors[1] + distance),
    ]


def get_possible_cors(selected_piece, gird):
    cors = get_cors_by_distance(selected_piece, 2)
    # within the border and no other pieces
    cors = [
        cor if cor in gird.keys() and gird[cor]['piece'] is None else None
        for cor in cors
    ]
    # print("cors within border:", cors)

    # follow the rule
    neighbor_cors = get_cors_by_distance(selected_piece, 1)
    indices = [
        i for i, neighbor_cor in enumerate(neighbor_cors)
        if neighbor_cor in gird.keys() and gird[neighbor_cor]['piece'] is not None
    ]
    cors = [cors[i] for i in indices]
    cors = [cor for cor in cors if cor is not None]
    # print("Possible cors: ", cors)
    return cors

