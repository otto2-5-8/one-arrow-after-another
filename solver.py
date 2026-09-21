"""关卡求解器：用来校验关卡可通关，也用于游戏里的提示功能。"""

from logic import DIRS


def free_in(state, dirs, pos, rows, cols):
    """state 是当前还在棋盘上的箭头位置，dirs 提供每个箭头的方向。"""
    dr, dc = DIRS[dirs[pos]]
    r, c = pos[0] + dr, pos[1] + dc
    while 0 <= r < rows and 0 <= c < cols:
        if (r, c) in state:
            return False
        r += dr
        c += dc
    return True


def solve(layout, rows, cols):
    """layout 是 {位置: 方向} 的字典，返回一个清空棋盘的点击顺序，无解返回 None。"""
    memo = {}

    def dfs(state):
        if not state:
            return []
        if state in memo:
            return memo[state]
        memo[state] = None
        for pos in sorted(state):
            if free_in(state, layout, pos, rows, cols):
                rest = dfs(frozenset(p for p in state if p != pos))
                if rest is not None:
                    memo[state] = [pos] + rest
                    return memo[state]
        return None

    return dfs(frozenset(layout))


def hint(game):
    """给出当前局面下不会走进死局的一步，找不到时退回任意可飞出的箭头。"""
    order = solve(game.arrows, game.rows, game.cols)
    if order:
        return order[0]
    free = game.free_arrows()
    return free[0] if free else None
