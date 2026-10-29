"""贪吃蛇游戏 (Snake Game)

使用方向键或 WASD 控制移动，吃到食物变长并加分。
按空格键暂停 / 继续，按 R 键重新开始，按 Esc 退出。
"""

import os
import random
import sys

import pygame

# 游戏配置
CELL_SIZE = 20          # 每个格子的像素大小
GRID_WIDTH = 30         # 横向格子数
GRID_HEIGHT = 24        # 纵向格子数
# 难度配置：名称、说明、初始速度、最高速度（速度单位 = 每秒移动的格数）
DIFFICULTIES = [
    {"name": "简单", "desc": "慢",   "base": 7,  "max": 16},
    {"name": "普通", "desc": "适中", "base": 10, "max": 24},
    {"name": "困难", "desc": "快",   "base": 14, "max": 30},
]

# 颜色
BACKGROUND = (24, 26, 32)
GRID_LINE = (40, 44, 54)
SNAKE_HEAD = (66, 211, 110)
SNAKE_BODY = (48, 160, 88)
FOOD = (255, 82, 82)
TEXT = (230, 235, 245)
TEXT_DIM = (140, 148, 162)

# 按键 -> 方向映射（方向键和 WASD 都支持）
TURNS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(
            (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE + 40)
        )
        pygame.display.set_caption("贪吃蛇")
        self.clock = pygame.time.Clock()
        self.font = self._load_font(20)
        self.difficulty_index = 1   # 当前难度：0 简单 / 1 普通 / 2 困难
        self.menu_index = 1         # 菜单里当前高亮的那一项
        self.in_menu = True         # 是否处于菜单界面
        self.reset()

    @staticmethod
    def _load_font(size):
        """加载中文字体；找不到时回退到 pygame 默认字体。

        不使用 pygame.font.SysFont，因为它在部分 Windows + Python 3.13
        环境下扫描系统字体时会报错（TypeError: expected str ... not int）。
        """
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return pygame.font.Font(path, size)
                except pygame.error:
                    continue
        return pygame.font.Font(None, size)

    def reset(self):
        """重置到初始状态。"""
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        # 蛇身：从蛇头开始的一串坐标（列表首元素是蛇头）
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)      # 当前移动方向
        self.next_direction = (1, 0)
        self.score = 0
        diff = DIFFICULTIES[self.difficulty_index]
        self.speed = diff["base"]
        self.max_speed = diff["max"]
        self.game_over = False
        self.paused = False
        self.started = False       # 是否已开始（未开始前蛇不动）
        self.food = self._spawn_food()

    def _spawn_food(self):
        """在空白位置随机生成食物。"""
        empty = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake
        ]
        return random.choice(empty)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif self.in_menu:
                    self._handle_menu_key(event.key)
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.game_over:
                    self.reset()
                elif not self.game_over and not self.paused:
                    if self._set_direction(event.key):
                        self.started = True

    def _set_direction(self, key):
        """根据按键设置下一个方向，返回是否设置了有效方向。"""
        if key not in TURNS:
            return False
        ndx, ndy = TURNS[key]
        dx, dy = self.direction
        # 禁止直接反向移动
        if (ndx, ndy) != (-dx, -dy):
            self.next_direction = (ndx, ndy)
            return True
        return False

    def _handle_menu_key(self, key):
        """菜单界面：↑↓ 切换难度，回车确认。"""
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(DIFFICULTIES)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(DIFFICULTIES)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.difficulty_index = self.menu_index
            self.in_menu = False
            self.reset()

    def _poll_direction(self):
        """兜底读取当前按住的键（避免个别环境下 KEYDOWN 事件丢失）。"""
        if self.in_menu:
            return
        pressed = pygame.key.get_pressed()
        for key, (ndx, ndy) in TURNS.items():
            if pressed[key]:
                if (ndx, ndy) != (-self.direction[0], -self.direction[1]):
                    self.next_direction = (ndx, ndy)
                if not self.started:
                    self.started = True
                break

    def update(self):
        if self.in_menu or self.game_over or self.paused or not self.started:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 撞墙判定
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        # 撞到自己判定（新蛇头不能撞到除蛇尾外的身体；蛇尾即将移开）
        if new_head in self.snake[:-1]:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            # 每吃 3 个食物加速一次
            if self.score % 3 == 0 and self.speed < self.max_speed:
                self.speed += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()  # 未吃到食物，移除蛇尾

    def draw(self):
        self.window.fill(BACKGROUND)

        # 绘制网格
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.window, GRID_LINE, rect, 1)

        # 绘制食物
        fx, fy = self.food
        pygame.draw.rect(
            self.window,
            FOOD,
            pygame.Rect(fx * CELL_SIZE + 3, fy * CELL_SIZE + 3,
                        CELL_SIZE - 6, CELL_SIZE - 6),
            border_radius=4,
        )

        # 绘制蛇
        for i, (sx, sy) in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(
                self.window,
                color,
                pygame.Rect(sx * CELL_SIZE + 1, sy * CELL_SIZE + 1,
                            CELL_SIZE - 2, CELL_SIZE - 2),
                border_radius=5,
            )

        if self.in_menu:
            self._draw_menu()
        else:
            self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        score_text = self.font.render(f"得分: {self.score}", True, TEXT)
        speed_text = self.font.render(f"速度: {self.speed}", True, TEXT_DIM)
        self.window.blit(score_text, (10, GRID_HEIGHT * CELL_SIZE + 8))
        self.window.blit(
            speed_text,
            (GRID_WIDTH * CELL_SIZE - 100, GRID_HEIGHT * CELL_SIZE + 8),
        )

        diff_text = self.font.render(
            f"难度: {DIFFICULTIES[self.difficulty_index]['name']}", True, TEXT_DIM
        )
        self.window.blit(
            diff_text,
            diff_text.get_rect(
                center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE + 18)
            ),
        )

        if not self.started and not self.game_over:
            self._draw_center_text("按方向键或 WASD 开始（请先点击窗口）", TEXT)
        elif self.paused and not self.game_over:
            self._draw_center_text("已暂停 - 按空格继续", TEXT)
        elif self.game_over:
            self._draw_center_text(
                f"游戏结束！得分 {self.score} - 按 R 或回车重新开始", FOOD
            )

    def _draw_menu(self):
        """绘制难度选择菜单。"""
        cx = GRID_WIDTH * CELL_SIZE // 2
        cy = GRID_HEIGHT * CELL_SIZE // 2

        title = self.font.render("选择难度", True, TEXT)
        self.window.blit(title, title.get_rect(center=(cx, cy - 80)))

        for i, diff in enumerate(DIFFICULTIES):
            selected = (i == self.menu_index)
            color = TEXT if selected else TEXT_DIM
            prefix = "> " if selected else "  "
            label = f"{prefix}{diff['name']}（{diff['desc']}，速度 {diff['base']}）"
            text = self.font.render(label, True, color)
            self.window.blit(text, text.get_rect(center=(cx, cy - 30 + i * 30)))

        hint = self.font.render("↑↓ 选择  回车确认", True, TEXT_DIM)
        self.window.blit(hint, hint.get_rect(center=(cx, cy + 70)))

    def _draw_center_text(self, message, color):
        surf = self.font.render(message, True, color)
        rect = surf.get_rect(
            center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2)
        )
        self.window.blit(surf, rect)

    def run(self):
        while True:
            self.handle_events()
            self._poll_direction()
            self.update()
            self.draw()
            self.clock.tick(self.speed)


if __name__ == "__main__":
    SnakeGame().run()
