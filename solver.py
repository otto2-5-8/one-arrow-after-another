"""关卡求解器：位掩码状态压缩 + 记忆化搜索。

每个箭头占一个二进制位，预先算出"这个箭头前进方向上有哪些箭头"的遮挡掩码，
于是"它现在能不能飞出"退化成一次按位与：blocks[i] & mask == 0。
搜索时 memo 只记录"这个局面选哪一步能赢"，最后回溯还原完整顺序；
再配上记忆化计数，就能数出"这一关一共有多少种通关顺序"。
"""

from logic import DIRS


def build(layout, rows, cols):
    """把 {位置: 方向} 编译成 (箭头列表, 遮挡位掩码列表)。"""
    cells = sorted(layout)
    index = {pos: i for i, pos in enumerate(cells)}
    blocks = []
    for pos in cells:
        dr, dc = DIRS[layout[pos]]
        r, c = pos[0] + dr, pos[1] + dc
        mask = 0
        while 0 <= r < rows and 0 <= c < cols:
            j = index.get((r, c))
            if j is not None:
                mask |= 1 << j
            r += dr
            c += dc
        blocks.append(mask)
    return cells, blocks


def free_in(state, dirs, pos, rows, cols):
    """朴素的线性扫描判空，保留下来给位掩码版本做对照校验。"""
    dr, dc = DIRS[dirs[pos]]
    r, c = pos[0] + dr, pos[1] + dc
    while 0 <= r < rows and 0 <= c < cols:
        if (r, c) in state:
            return False
        r += dr
        c += dc
    return True


def moves(mask, blocks):
    """当前局面下所有能飞出的箭头下标。"""
    return [i for i, block in enumerate(blocks) if mask >> i & 1 and not block & mask]


def search(cells, blocks, mask):
    """记忆化搜索，返回 (箭头下标顺序 或 None, 搜索过的局面数)。"""
    memo = {}
    visits = [0]

    def dfs(state):
        if state == 0:
            return True
        if state in memo:
            return memo[state] >= 0
        visits[0] += 1
        for i in moves(state, blocks):
            if dfs(state ^ (1 << i)):
                memo[state] = i
                return True
        memo[state] = -1
        return False

    if not dfs(mask):
        return None, visits[0]
    order = []
    state = mask
    while state:
        i = memo[state]
        order.append(i)
        state ^= 1 << i
    return order, visits[0]


def count_orders(cells, blocks, mask):
    """记忆化计数：ways(局面) = 所有可行着法的 ways 之和，ways(空盘) = 1。"""
    memo = {0: 1}

    def ways(state):
        if state in memo:
            return memo[state]
        total = 0
        for i in moves(state, blocks):
            total += ways(state ^ (1 << i))
        memo[state] = total
        return total

    return ways(mask)


def solve(layout, rows, cols):
    """layout 是 {位置: 方向} 的字典，返回一个清空棋盘的点击顺序，无解返回 None。"""
    cells, blocks = build(layout, rows, cols)
    order, _ = search(cells, blocks, (1 << len(cells)) - 1)
    return None if order is None else [cells[i] for i in order]


def analyze(layout, rows, cols):
    """统计难度指标：箭头数、初始可飞出数、通关顺序总数、搜索过的局面数。"""
    cells, blocks = build(layout, rows, cols)
    full = (1 << len(cells)) - 1
    order, visits = search(cells, blocks, full)
    total = count_orders(cells, blocks, full)
    return {
        "arrows": len(cells),
        "first_free": len(moves(full, blocks)),
        "solvable": order is not None,
        "orders": total,
        "unique": total == 1,
        "states": visits,
    }


def hint(game):
    """给出当前局面下不会走进死局的一步，找不到时退回任意可飞出的箭头。"""
    cells, blocks = build(game.arrows, game.rows, game.cols)
    order, _ = search(cells, blocks, (1 << len(cells)) - 1)
    if order:
        return cells[order[0]]
    free = game.free_arrows()
    return free[0] if free else None
