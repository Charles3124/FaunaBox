# resources.py
"""游戏资源系统"""

import pygame

from game.utils import get_font


class ResourceManager:
    """管理游戏资源，实现三类资源的获取"""

    eco_interval = 8000   # 随时间获得生态点
    
    def __init__(self, font_name: str = "SimSun", font_size: int = 20, position: tuple[int, int] = (500, 20), test: bool = False):
        self.leafium = 0    # 绿素：植物贡献
        self.animite = 0    # 兽能：动物贡献
        self.ecopoint = 0   # 生态点：时间线性增长

        if test:
            self.leafium = self.animite = self.ecopoint = 1000

        self.active_time = 0
        self.last_update_time = pygame.time.get_ticks()

        self.font = get_font(font_name, font_size)
        self.position = position

    def gain_leafium(self, amount: int = 1) -> None:
        """增加绿素"""
        self.leafium += amount

    def gain_animite(self, amount: int = 1) -> None:
        """增加兽能"""
        self.animite += amount

    def update_ecopoints(self, time_speed: int, pause: bool) -> None:
        """更新生态点"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now
        if pause:
            return

        delta_time *= time_speed
        self.active_time += delta_time
        if self.active_time > self.eco_interval:
            self.active_time = 0
            self.ecopoint += 1

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制资源"""
        text = f"绿素 {self.leafium}  兽能 {self.animite}  生态点 {self.ecopoint}"
        surface = self.font.render(text, True, (0, 0, 0))
        screen.blit(surface, self.position)
