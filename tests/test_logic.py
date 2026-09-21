"""自动化测试：对应作业里的 T01-T06。"""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

import main as game_module  # noqa: E402
import solver  # noqa: E402
from levels import LEVELS  # noqa: E402
from logic import GameState  # noqa: E402


def make(grid):
    return GameState({"name": "测试关", "mistakes": 3, "grid": grid})


class TestPathDetection(unittest.TestCase):
    """T01-T03：路径检测与边界情况。"""

    def test_t01_click_free_arrow(self):
        game = make(["..>..", ".v..."])
        self.assertTrue(game.is_free((0, 2)))
        self.assertEqual(game.click((0, 2)), "escape")
        self.assertEqual(game.remaining, 1)
        self.assertEqual(game.mistakes, 3)
        self.assertIsNone(game.result)

    def test_t02_click_blocked_arrow(self):
        game = make(["..>.>", "....."])
        self.assertFalse(game.is_free((0, 2)))
        self.assertEqual(game.click((0, 2)), "blocked")
        self.assertEqual(game.remaining, 2)
        self.assertEqual(game.mistakes, 2)
        self.assertEqual(game.click((0, 4)), "escape")

    def test_t03_edge_arrows(self):
        game = make(["^....", ".....", "<...>", ".....", ".^..v"])
        for cell in [(0, 0), (2, 0), (2, 4), (4, 1), (4, 4)]:
            self.assertTrue(game.is_free(cell), cell)
        for cell in [(0, 0), (2, 0), (2, 4), (4, 1), (4, 4)]:
            self.assertEqual(game.click(cell), "escape")
        self.assertEqual(game.result, "win")

    def test_all_directions_blocked_by_ray(self):
        game = make(["..v..", "..v.<", "<.<.>", "..^>v", "..^.."])
        for cell in [(0, 2), (1, 2), (1, 4), (2, 2), (3, 2), (3, 3), (4, 2)]:
            self.assertFalse(game.is_free(cell), cell)
        for cell in [(2, 0), (2, 4), (3, 4)]:
            self.assertTrue(game.is_free(cell), cell)
        self.assertEqual(game.click((0, 2)), "blocked")
        self.assertEqual(game.mistakes, 2)

    def test_levels_are_solvable(self):
        for level in LEVELS:
            game = GameState(level)
            order = solver.solve(game.arrows, game.rows, game.cols)
            self.assertIsNotNone(order, level["name"])
            self.assertEqual(len(order), game.total, level["name"])


class TestLevelFlow(unittest.TestCase):
    """T04-T06：过关、失败和重新开始。"""

    def setUp(self):
        self.app = game_module.App()

    def tearDown(self):
        pygame.quit()

    def clear_level(self):
        while not self.app.game.result:
            cells = self.app.game.free_arrows()
            self.assertTrue(cells)
            self.app.click_board(cells[0])

    def test_t04_clear_level_and_next(self):
        app = self.app
        app.start_level(0)
        self.clear_level()
        self.assertEqual(app.game.result, "win")
        self.assertEqual(app.game.remaining, 0)
        app.update(game_module.OVERLAY_DELAY + 0.2)
        self.assertEqual(app.overlay, "win")
        self.assertEqual(app.unlocked, 2)
        app.next_level()
        self.assertEqual(app.level_index, 1)
        self.assertIsNone(app.game.result)
        self.assertEqual(app.game.remaining, app.game.total)

    def test_t05_mistakes_run_out(self):
        app = self.app
        app.start_level(1)
        blocked = [p for p in app.game.arrows if not app.game.is_free(p)]
        self.assertTrue(blocked)
        while app.game.result is None:
            app.click_board(blocked[0])
        self.assertEqual(app.game.result, "lose")
        self.assertEqual(app.game.mistakes, 0)
        app.update(game_module.OVERLAY_DELAY + 0.2)
        self.assertEqual(app.overlay, "lose")

    def test_t06_restart_restores_level(self):
        app = self.app
        app.start_level(0)
        total = app.game.total
        app.click_board(app.game.free_arrows()[0])
        blocked = [p for p in app.game.arrows if not app.game.is_free(p)][0]
        app.click_board(blocked)
        self.assertEqual(app.game.remaining, total - 1)
        self.assertEqual(app.game.mistakes, app.game.max_mistakes - 1)
        app.restart_level()
        self.assertEqual(app.game.remaining, total)
        self.assertEqual(app.game.mistakes, app.game.max_mistakes)
        self.assertIsNone(app.game.result)
        self.assertEqual(app.flyers, [])
        self.assertEqual(app.elapsed, 0.0)

    def test_on_click_maps_pixel_to_cell(self):
        """点击事件的坐标换算：格子里算点中，格子缝隙里不算。"""
        app = self.app
        app.start_level(0)
        self.assertEqual(app.game.free_arrows(), [(4, 2)])
        app.on_click(app.cell_rect(4, 2).center)
        self.assertNotIn((4, 2), app.game.arrows)
        self.assertEqual(app.game.remaining, app.game.total - 1)
        app.on_click(app.cell_rect(1, 2).center)
        self.assertIn((1, 2), app.game.arrows)
        self.assertEqual(app.game.mistakes, app.game.max_mistakes - 1)
        gap = app.cell_rect(1, 2)
        app.on_click((gap.right + 3, gap.centery))
        self.assertEqual(app.game.mistakes, app.game.max_mistakes - 1)

    def test_click_hint_button(self):
        app = self.app
        app.start_level(0)
        app.draw()
        button = [b for b in app.buttons if "提示" in b.label][0]
        app.on_click(button.rect.center)
        self.assertIn(app.hint, app.game.arrows)

    def test_undo_puts_arrow_back(self):
        app = self.app
        app.start_level(0)
        cell = app.game.free_arrows()[0]
        app.click_board(cell)
        app.use_undo()
        self.assertIn(cell, app.game.arrows)
        self.assertEqual(app.game.remaining, app.game.total)
        self.assertIsNone(app.game.result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
