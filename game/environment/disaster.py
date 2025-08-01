# disaster.py
import pygame
import math
import random
from ..utils.config import MapConfig

class DisasterManager:

    def __init__(self, disaster_interval=20000, font_size=20, font_name="SimSun"):
        self.font = pygame.font.SysFont(font_name, font_size)

        self.disaster_interval = disaster_interval        # 灾害间隔
        self.active_time = 0                              # 活跃时间
        self.last_update_time = pygame.time.get_ticks()   # 上次更新时间

        self.current_disaster_text = None   # 灾害文字提醒
        self.active_draw_time = 0           # 灾害显示的活跃时间
        self.last_draw_time = pygame.time.get_ticks()    # 上次灾害显示的时间
        self.draw_duration = 4000           # 闪烁时长
        self.hold_duration = 3000           # 常亮时长
        self.fadeout_duration = 1000        # 淡出时长
        self.total_duration = self.draw_duration + self.hold_duration + self.fadeout_duration   # 总时长
        self.cycle_count = 3                # 闪烁次数
        self.max_alpha = 180                # 最大透明度

        self.max_disaster_time = 50     # 下一次灾难来袭的最大时间
        self.min_disaster_time = 30     # 下一次灾难来袭的最小时间

        self.disasters = [
            self.animal_plague
        ]

    def update(self, world, time_speed, pause):
        """检查是否触发灾害"""
        # 只有没有灾害时，才检查是否生成灾害，并累计时间
        if self.current_disaster_text is not None:
            return

        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = pygame.time.get_ticks()
        if pause:
            return
        delta_time *= time_speed
        self.active_time += delta_time

        # 如果大于阈值，则生成灾害
        if self.active_time > self.disaster_interval:
            self.active_time = 0
            self.trigger_random_disaster(world)

    def trigger_random_disaster(self, world):
        """随机触发一个灾害"""
        disaster = random.choice(self.disasters)
        disaster(world)

    def finish_disaster(self):
        """结束灾害"""
        self.current_disaster_text = None
        self.active_draw_time = 0
        self.last_update_time = pygame.time.get_ticks()
        self.disaster_interval = 1000 * random.randrange(self.min_disaster_time, self.max_disaster_time)

    def animal_plague(self, world):
        """动物感染瘟疫"""
        candidates = [r for r in world.rabbits if not r.infected]
        if not candidates:
            return

        to_infect = random.sample(candidates, min(len(candidates), random.randint(1, 2)))
        for r in to_infect:
            r.infect(world.rabbit_config.image_infected)
        self.set_disaster_message("兔子感染瘟疫！")

    def set_disaster_message(self, text):
        """记录灾害文本并启动显示计时"""
        self.current_disaster_text = text
        self.active_draw_time = 0
        self.last_draw_time = pygame.time.get_ticks()

    def draw(self, screen, time_speed, pause):
        """绘制灾害提示框（闪烁 + 常亮 + 淡出）"""
        # 只有存在灾害时，才绘制灾害
        if self.current_disaster_text is None:
            return

        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_draw_time
        self.last_draw_time = now
        if pause:
            delta_time = 0
        delta_time *= time_speed
        self.active_draw_time += delta_time

        if self.active_draw_time > self.total_duration:
            self.finish_disaster()
            return

        # 渲染文字表面
        text_surface = self.font.render(self.current_disaster_text, True, (200, 50, 50))
        text_rect = text_surface.get_rect()

        padding_x = 20
        padding_y = 10
        box_width = text_rect.width + 2 * padding_x
        box_height = text_rect.height + 2 * padding_y
        x = MapConfig.width - 300 - box_width // 2
        y = 10
        
        # 阶段一：闪烁
        if self.active_draw_time <= self.draw_duration:
            flicker_time = self.active_draw_time
            if flicker_time < self.draw_duration - 1000:
                t = (flicker_time / self.draw_duration) * self.cycle_count * math.pi
                alpha = int((math.sin(t) ** 2) * 255)
            else:
                # 渐亮过渡：线性从当前 alpha 到 255
                progress = (flicker_time - (self.draw_duration - 500)) / 500
                t = ((self.draw_duration - 500) / self.draw_duration) * self.cycle_count * math.pi
                base_alpha = int((math.sin(t) ** 2) * 255)
                alpha = int(base_alpha + (255 - base_alpha) * progress)

        # 阶段二：常亮
        elif self.active_draw_time <= self.draw_duration + self.hold_duration:
            alpha = 255

        # 阶段三：淡出
        else:
            fade_elapsed = self.active_draw_time - (self.draw_duration + self.hold_duration)
            fade_ratio = max(0, 1 - fade_elapsed / self.fadeout_duration)
            alpha = int(255 * fade_ratio)

        # 绘制半透明白框
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((255, 255, 255, min(self.max_alpha, alpha)))
        screen.blit(box_surface, (x, y))

        # 绘制半透明文字
        text_surface.set_alpha(alpha)
        text_rect.center = (x + box_width // 2, y + box_height // 2)
        screen.blit(text_surface, text_rect)
