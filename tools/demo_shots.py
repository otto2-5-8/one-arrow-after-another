"""按固定剧本驱动界面走一遍，配合 capture_window.ps1 自动截图。"""

import os
import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main as game  # noqa: E402

MARKER = os.environ.get("DEMO_MARKER")


def first_free(app):
    free = app.game.free_arrows()
    return free[0] if free else None


def first_blocked(app):
    for pos in sorted(app.game.arrows):
        if not app.game.is_free(pos):
            return pos
    return None


def click_flying(app, offset=0.6):
    """点掉一个能飞出的箭头，冻结画面并把箭头停在半空中。"""
    cell = first_free(app)
    if cell is None:
        return
    app.click_board(cell)
    app.freeze(True)
    if app.flyers:
        rect = app.cell_rect(*cell)
        flyer = app.flyers[-1]
        dr, dc = game.DIRS[flyer["dir"]]
        flyer["x"] = rect.centerx + dc * rect.width * offset
        flyer["y"] = rect.centery + dr * rect.height * offset


def click_blocked(app):
    cell = first_blocked(app)
    if cell is None:
        return
    app.click_board(cell)
    app.freeze(True)


def build_plan():
    return [
        (3.0, lambda a: a.start_level(0)),
        (6.0, lambda a: click_flying(a)),
        (8.0, lambda a: a.freeze(False)),
        (8.6, lambda a: click_blocked(a)),
        (11.5, lambda a: a.freeze(False)),
        (12.5, lambda a: a.start_level(4)),
        (12.6, lambda a: setattr(a, "keep_hint", True)),
        (17.0, lambda a: setattr(a, "keep_hint", False)),
        (17.5, lambda a: a.start_level(3)),
        (17.9, lambda a: setattr(a, "auto_play", True)),
        (26.5, lambda a: (setattr(a, "auto_play", False), a.start_level(0))),
        (26.8, lambda a: [a.click_board(first_blocked(a)) for _ in range(3)]),
        (31.5, lambda a: setattr(a, "running", False)),
    ]


class DemoApp(game.App):
    def __init__(self, plan):
        super().__init__()
        self.plan = plan
        self.t = 0.0
        self.t0 = None
        self.idx = 0
        self.frozen = False
        self.auto_play = False
        self.last_auto = 0.0
        self.keep_hint = False
        self.last_hint = 0.0
        self.marked = False

    def freeze(self, flag):
        self.frozen = flag

    def update(self, dt):
        if self.t0 is None:
            self.t0 = pygame.time.get_ticks()
        self.t = (pygame.time.get_ticks() - self.t0) / 1000.0
        while self.idx < len(self.plan) and self.t >= self.plan[self.idx][0]:
            self.plan[self.idx][1](self)
            self.idx += 1
        if self.auto_play and self.game and not self.game.result:
            if self.t - self.last_auto > 0.30:
                self.last_auto = self.t
                cell = first_free(self)
                if cell:
                    self.click_board(cell)
        if self.keep_hint and self.game and not self.game.result:
            if self.t - self.last_hint > 0.7:
                self.last_hint = self.t
                self.use_hint()
        if not self.frozen:
            super().update(dt)

    def draw(self):
        if not self.marked and MARKER:
            self.marked = True
            Path(MARKER).write_text("ready", encoding="utf-8")
        super().draw()


if __name__ == "__main__":
    DemoApp(build_plan()).run()
