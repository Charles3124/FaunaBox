# building.py
import pygame

class Building:

    def __init__(self, name, image_path, pos, size):
        self.name = name
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path).convert_alpha(), size)
        self.pos = pos
        self.visible = False

    def draw(self, screen):
        """绘制建筑"""
        if self.visible:
            rect = self.image.get_rect(center=self.pos)
            screen.blit(self.image, rect)
