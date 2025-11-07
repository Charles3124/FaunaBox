"""
disaster.py

功能: 游戏灾害系统
时间: 2025/11/07
版本: 1.0
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import math
import random

import pygame

from game.utils import (MapConfig, get_font)
from .season import Season


if TYPE_CHECKING:
    from game.core import World


class DisasterManager:
    """管理灾害开始、结束等事件"""

    def __init__(self, disaster_interval: int = 20000, font_name: str = "SimSun", font_size: int = 20):
        self.font = get_font(font_name, font_size)

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

        self.mid_state = None    # 中转状态
        self.disasters = {
            "animal_plague": {"func": self.animal_plague, "message": "兔子感染瘟疫！"},
            "harsh_winter": {"func": self.harsh_winter, "message": "严冬来临！"},
        }

    def update(self, world: World, season: Season, time_speed: int, pause: bool) -> None:
        """检查是否触发灾害"""
        # 判断当前是否是中转状态
        if self.mid_state == "animal_plague":
            self.start_disaster(world)
        
        elif self.mid_state == "harsh_winter":
            if season.current == "冬天":
                self.start_disaster(world)
        
        else:
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
                self.choose_random_disaster()

    def choose_random_disaster(self) -> None:
        """随机触发一个灾害"""
        self.mid_state = random.choice(list(self.disasters.keys()))

    def start_disaster(self, world: World) -> None:
        """开始灾害与提示文字"""
        func = self.disasters[self.mid_state]["func"]
        func(world)
        message = self.disasters[self.mid_state]["message"]
        self.set_disaster_message(message)
        self.start_disaster_timer()

    def start_disaster_timer(self) -> None:
        """开始下一次灾害的计时"""
        self.mid_state = None
        self.active_time = 0
        self.last_update_time = pygame.time.get_ticks()
        self.disaster_interval = 1000 * random.randrange(self.min_disaster_time, self.max_disaster_time)

    def set_disaster_message(self, text: str) -> None:
        """记录灾害文本并启动显示计时"""
        self.current_disaster_text = text
        self.active_draw_time = 0
        self.last_draw_time = pygame.time.get_ticks()

    def animal_plague(self, world: World) -> None:
        """动物感染瘟疫"""
        candidates = [r for r in world.rabbits if not r.infected]
        if not candidates:
            return

        to_infect = random.sample(candidates, min(len(candidates), random.randint(1, 2)))
        for r in to_infect:
            r.infect(world.rabbit_config.image_infected)

    def harsh_winter(self, world: World) -> None:
        """冬天延长，植物更容易死亡"""
        world.season.active_time -= 5000
        world.plant_config.is_fragile = True

    def draw(self, screen: pygame.surface.Surface, time_speed: int, pause: bool) -> None:
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
            self.current_disaster_text = None
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
            fade_ratio = max(0.0, 1 - fade_elapsed / self.fadeout_duration)
            alpha = int(255 * fade_ratio)

        # 绘制半透明白框
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((255, 255, 255, min(self.max_alpha, alpha)))
        screen.blit(box_surface, (x, y))

        # 绘制半透明文字
        text_surface.set_alpha(alpha)
        text_rect.center = (x + box_width // 2, y + box_height // 2)
        screen.blit(text_surface, text_rect)
