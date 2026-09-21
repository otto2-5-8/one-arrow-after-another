"""游戏核心逻辑，不依赖图形库，方便单独测试。

判空用"行/列有序坐标表 + 二分查找"：每行、每列各维护一个升序列表，
查询某箭头前方还有没有箭头时，只需二分出它在列表中的位置再看是否为边界。
"""

import bisect

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
        self.row_cols = {}
        self.col_rows = {}
        for r, line in enumerate(self.grid):
            for c, ch in enumerate(line):
                if ch in DIRS:
                    self._place((r, c), ch)
        self.total = len(self.arrows)
        self.mistakes = self.max_mistakes
        self.history = []
        self.result = None

    def _place(self, pos, direction):
        """放回一个箭头，并把它的行、列坐标插进有序表（insort 保证仍然升序）。"""
        r, c = pos
        self.arrows[pos] = direction
        bisect.insort(self.row_cols.setdefault(r, []), c)
        bisect.insort(self.col_rows.setdefault(c, []), r)

    def _take(self, pos):
        """拿走一个箭头：先二分定位，再从两个有序表里删掉。"""
        r, c = pos
        del self.arrows[pos]
        cols = self.row_cols[r]
        cols.pop(bisect.bisect_left(cols, c))
        rows = self.col_rows[c]
        rows.pop(bisect.bisect_left(rows, r))

    @property
    def remaining(self):
        return len(self.arrows)

    def is_free(self, pos):
        """箭头到棋盘边界之间没有其它箭头时返回 True。"""
        dr, dc = DIRS[self.arrows[pos]]
        r, c = pos
        if dr == 0:
            line = self.row_cols[r]
            forward = dc > 0
            index = bisect.bisect_right(line, c) if forward else bisect.bisect_left(line, c)
        else:
            line = self.col_rows[c]
            forward = dr > 0
            index = bisect.bisect_right(line, r) if forward else bisect.bisect_left(line, r)
        return index == len(line) if forward else index == 0

    def free_arrows(self):
        return [pos for pos in self.arrows if self.is_free(pos)]

    def click(self, pos):
        if self.result or pos not in self.arrows:
            return "ignored"
        if self.is_free(pos):
            self.history.append(pos)
            self._take(pos)
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
        self._place(pos, self.grid[pos[0]][pos[1]])
        self.result = None
        return pos
