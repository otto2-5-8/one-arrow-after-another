"""游戏核心逻辑，不依赖图形库，方便单独测试。"""

DIRS = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


class GameState:
    def __init__(self, level):
        self.name = level["name"]
        self.grid = level["grid"]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.max_mistakes = level.get("mistakes", 3)
        self.reset()

    def reset(self):
        self.arrows = {}
        for r, line in enumerate(self.grid):
            for c, ch in enumerate(line):
                if ch in DIRS:
                    self.arrows[(r, c)] = ch
        self.total = len(self.arrows)
        self.mistakes = self.max_mistakes
        self.history = []
        self.result = None

    @property
    def remaining(self):
        return len(self.arrows)

    def is_free(self, pos):
        """箭头到棋盘边界之间没有其它箭头时返回 True。"""
        dr, dc = DIRS[self.arrows[pos]]
        r, c = pos[0] + dr, pos[1] + dc
        while 0 <= r < self.rows and 0 <= c < self.cols:
            if (r, c) in self.arrows:
                return False
            r += dr
            c += dc
        return True

    def free_arrows(self):
        return [pos for pos in self.arrows if self.is_free(pos)]

    def click(self, pos):
        if self.result or pos not in self.arrows:
            return "ignored"
        if self.is_free(pos):
            self.history.append(pos)
            del self.arrows[pos]
            if not self.arrows:
                self.result = "win"
            return "escape"
        self.mistakes -= 1
        if self.mistakes <= 0:
            self.mistakes = 0
            self.result = "lose"
        return "blocked"

    def undo(self):
        if self.result == "lose" or not self.history:
            return None
        pos = self.history.pop()
        self.arrows[pos] = self.grid[pos[0]][pos[1]]
        self.result = None
        return pos
