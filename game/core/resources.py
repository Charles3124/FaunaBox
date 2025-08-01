# resources.py
import pygame

class ResourceManager:
    eco_interval = 8000   # 随时间获得生态点
    
    def __init__(self, font_name="SimSun", font_size=20, position = (500, 20), test=False):
        if not test:
            self.leafium = 0    # 绿素：植物贡献
            self.animite = 0    # 兽能：动物贡献
            self.ecopoint = 0   # 生态点：时间线性增长
        else:
            self.leafium = 1000    # 绿素：植物贡献
            self.animite = 1000    # 兽能：动物贡献
            self.ecopoint = 1000   # 生态点：时间线性增长

        self.active_time = 0
        self.last_update_time = pygame.time.get_ticks()

        self.font = pygame.font.SysFont(font_name, font_size)
        self.position = position

    def gain_leafium(self, amount=1):
        """增加绿素"""
        self.leafium += amount

    def gain_animite(self, amount=1):
        """增加兽能"""
        self.animite += amount

    def update_ecopoints(self, time_speed, pause):
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

    def draw(self, screen):
        """绘制资源"""
        text = f"绿素 {self.leafium}  兽能 {self.animite}  生态点 {self.ecopoint}"
        surface = self.font.render(text, True, (0, 0, 0))
        screen.blit(surface, self.position)
