# clock.py
"""游戏时间系统"""

import pygame

from game.utils import (color, get_font)


class Clock:
    """管理游戏暂停、倍速等事件"""
    
    def __init__(self, initial_speed: int, speeds: list[int]):
        self.years = 0
        self.months = 3
        self.month_time = 5000
        self.speed = initial_speed
        self.speeds = speeds
        self.font = get_font('SimSun', 24)
        self.last_update_time = pygame.time.get_ticks()
        self.elapsed_time = 0

    def update(self, pause: bool) -> None:
        """更新时间"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now
        if pause:
            return
        delta_time *= self.speed
        self.elapsed_time += delta_time

        if self.elapsed_time >= self.month_time:
            self.elapsed_time = 0
            self.months += 1

            if self.months > 12:
                self.months = 1
                self.years += 1

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制时间"""
        time_text = f"{self.years}年{self.months}月"
        text_surface = self.font.render(time_text, True, color.BLACK)
        screen.blit(text_surface, (11, 15))

    def change_speed(self) -> None:
        """切换倍速"""
        idx = self.speeds.index(self.speed)
        idx += 1
        if idx >= len(self.speeds):
            idx = 0
        self.speed = self.speeds[idx]
