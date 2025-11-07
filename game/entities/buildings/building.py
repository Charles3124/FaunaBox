"""
building.py

功能: 游戏建筑系统
时间: 2025/11/07
版本: 1.0
"""

import pygame


class Building:
    """创建和管理建筑实体"""

    def __init__(self, name: str, image_path: str, pos: tuple[int, int], size: tuple[int, int]):
        self.name = name
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path).convert_alpha(), size)
        self.pos = pos
        self.visible = False

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制建筑"""
        if self.visible:
            rect = self.image.get_rect(center=self.pos)
            screen.blit(self.image, rect)
