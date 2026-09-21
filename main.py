"""一箭又一箭 —— 点击式箭头解谜小游戏，用 pygame 实现。"""

import math
import sys

import pygame

from levels import LEVELS
from logic import DIRS, GameState

WIDTH, HEIGHT = 980, 760
FPS = 60

BG = (24, 28, 38)
CARD = (37, 44, 60)
CELL = (47, 56, 76)
TEXT = (233, 238, 248)
MUTED = (146, 158, 180)
GOLD = (247, 200, 92)
DANGER = (232, 96, 96)

ARROW_COLORS = {
    "^": (247, 200, 92),
    "v": (108, 200, 255),
    "<": (247, 132, 150),
    ">": (130, 214, 156),
}

BOARD_AREA = (60, 150, WIDTH - 120, 460)
FONT_NAMES = [
    "microsoftyaheiui",
    "microsoftyahei",
    "simhei",
    "simsun",
    "notosanscjksc",
    "wqy-microhei",
    "arialunicodems",
]

ARROW_SHAPE = [
    (0.0, -1.0),
    (0.62, -0.30),
    (0.26, -0.30),
    (0.26, 0.95),
    (-0.26, 0.95),
    (-0.26, -0.30),
    (-0.62, -0.30),
]
ARROW_ANGLE = {"^": 0, ">": 90, "v": 180, "<": 270}


def load_font(size, bold=False):
    path = pygame.font.match_font(FONT_NAMES, bold=bold)
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size)


def arrow_points(cx, cy, size, direction):
    angle = math.radians(ARROW_ANGLE[direction])
    ca, sa = math.cos(angle), math.sin(angle)
    return [
        (cx + (x * ca - y * sa) * size, cy + (x * sa + y * ca) * size)
        for x, y in ARROW_SHAPE
    ]


class Button:
    def __init__(self, rect, label, action):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("一箭又一箭")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.buttons = []
        self.running = True
        self.scene = "menu"
        self.level_index = 0
        self.game = None
        self.flyers = []

    def font(self, size, bold=False):
        if (size, bold) not in self.fonts:
            self.fonts[(size, bold)] = load_font(size, bold)
        return self.fonts[(size, bold)]

    def text(self, content, size, color=MUTED, center=None, topleft=None, bold=False):
        surf = self.font(size, bold).render(content, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = center
        if topleft:
            rect.topleft = topleft
        self.screen.blit(surf, rect)
        return rect

    def start_level(self, index):
        self.level_index = index
        self.game = GameState(LEVELS[index])
        self.scene = "game"
        self.flyers = []
        self.elapsed = 0.0

    def geometry(self):
        rows, cols = self.game.rows, self.game.cols
        ax, ay, aw, ah = BOARD_AREA
        gap = 10
        cell = min(
            (aw - gap * (cols + 1)) // cols,
            (ah - gap * (rows + 1)) // rows,
            84,
        )
        board_w = cell * cols + gap * (cols + 1)
        board_h = cell * rows + gap * (rows + 1)
        return cell, gap, ax + (aw - board_w) // 2, ay + (ah - board_h) // 2

    def cell_rect(self, r, c):
        cell, gap, ox, oy = self.geometry()
        return pygame.Rect(
            ox + gap + c * (cell + gap),
            oy + gap + r * (cell + gap),
            cell,
            cell,
        )

    def cell_at(self, pos):
        cell, gap, ox, oy = self.geometry()
        step = cell + gap
        c = (pos[0] - ox - gap) // step
        r = (pos[1] - oy - gap) // step
        if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
            if self.cell_rect(r, c).collidepoint(pos):
                return (r, c)
        return None

    def draw_arrow(self, center, size, direction, color, alpha=255):
        points = arrow_points(center[0], center[1], size, direction)
        if alpha >= 255:
            pygame.draw.polygon(self.screen, color, points)
            return
        side = int(size * 2.4)
        layer = pygame.Surface((side, side), pygame.SRCALPHA)
        local = [
            (x - center[0] + side / 2, y - center[1] + side / 2) for x, y in points
        ]
        pygame.draw.polygon(layer, color + (alpha,), local)
        self.screen.blit(layer, (center[0] - side / 2, center[1] - side / 2))

    def draw_menu(self):
        self.buttons = []
        self.screen.fill(BG)
        self.text("一箭又一箭", 68, GOLD, center=(WIDTH // 2, 200), bold=True)
        self.text(
            "点击能飞出去的箭头，把它们全部清出棋盘",
            24,
            MUTED,
            center=(WIDTH // 2, 268),
        )
        start = Button((WIDTH // 2 - 130, 330, 260, 66), "开始游戏", lambda: self.start_level(0))
        self.draw_button(start, size=28, primary=True)
        self.text("选择关卡", 20, MUTED, center=(WIDTH // 2, 452))
        for i in range(len(LEVELS)):
            rect = pygame.Rect(WIDTH // 2 - 300 + i * 120, 490, 100, 62)
            button = Button(rect, str(i + 1), (lambda idx: lambda: self.start_level(idx))(i))
            self.draw_button(button, size=26)
        self.text("R 重新开始    H 提示    Esc 返回菜单", 18, MUTED, center=(WIDTH // 2, 640))

    def draw_button(self, button, size=22, primary=False):
        hover = button.rect.collidepoint(pygame.mouse.get_pos())
        color = (GOLD if primary else CELL) if hover else (GOLD if primary else CARD)
        text_color = (30, 34, 46) if (primary or hover) else TEXT
        pygame.draw.rect(self.screen, color, button.rect, border_radius=12)
        self.text(button.label, size, text_color, center=button.rect.center, bold=hover)
        self.buttons.append(button)

    def draw_hud(self):
        self.text(f"{self.game.name}", 30, TEXT, topleft=(60, 46), bold=True)
        self.text(
            f"剩余箭头 {self.game.remaining} / {self.game.total}",
            22,
            MUTED,
            topleft=(60, 92),
        )
        self.text(f"第 {self.level_index + 1} / {len(LEVELS)} 关", 22, MUTED, topleft=(320, 92))

    def draw_board(self):
        cell, gap, ox, oy = self.geometry()
        rows, cols = self.game.rows, self.game.cols
        board = pygame.Rect(
            ox,
            oy,
            cell * cols + gap * (cols + 1),
            cell * rows + gap * (rows + 1),
        )
        pygame.draw.rect(self.screen, CARD, board, border_radius=18)
        for r in range(rows):
            for c in range(cols):
                pygame.draw.rect(self.screen, CELL, self.cell_rect(r, c), border_radius=8)
        for (r, c), direction in self.game.arrows.items():
            rect = self.cell_rect(r, c)
            self.draw_arrow(rect.center, rect.width * 0.62, direction, ARROW_COLORS[direction])

    def draw_game(self):
        self.buttons = []
        self.screen.fill(BG)
        self.draw_hud()
        self.draw_board()
        for flyer in self.flyers:
            self.draw_arrow(
                (flyer["x"], flyer["y"]),
                flyer["size"],
                flyer["dir"],
                flyer["color"],
                flyer["alpha"],
            )

    def draw(self):
        if self.scene == "menu":
            self.draw_menu()
        else:
            self.draw_game()
        pygame.display.flip()

    def click_board(self, cell):
        direction = self.game.arrows.get(cell)
        if direction is None:
            return
        if self.game.click(cell) == "escape":
            rect = self.cell_rect(*cell)
            self.flyers.append(
                {
                    "x": rect.centerx,
                    "y": rect.centery,
                    "dir": direction,
                    "size": rect.width * 0.62,
                    "color": ARROW_COLORS[direction],
                    "alpha": 255,
                }
            )

    def on_click(self, pos):
        for button in reversed(self.buttons):
            if button.rect.collidepoint(pos):
                button.action()
                return
        if self.scene == "game":
            cell = self.cell_at(pos)
            if cell:
                self.click_board(cell)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.scene = "menu"
                elif event.key == pygame.K_r and self.scene == "game":
                    self.game.reset()
                    self.flyers = []
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.on_click(event.pos)

    def update(self, dt):
        if self.scene == "game" and not self.game.result:
            self.elapsed += dt
        speed = 1500
        for flyer in self.flyers:
            flyer["y"] += DIRS[flyer["dir"]][0] * speed * dt
            flyer["x"] += DIRS[flyer["dir"]][1] * speed * dt
            flyer["alpha"] = max(0, flyer["alpha"] - 400 * dt)
        self.flyers = [
            f for f in self.flyers if -120 < f["x"] < WIDTH + 120 and -120 < f["y"] < HEIGHT + 120
        ]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        return 0


def main():
    sys.exit(App().run())


if __name__ == "__main__":
    main()
