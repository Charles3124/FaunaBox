# season.py
"""游戏季节和天气系统"""

import math
import random

import pygame

from game.utils import (color, MapConfig, sound_manager, get_font)


class Season:
    """管理四季更替、不定时降雨"""

    config = None
    SEASONS = ('春天', '夏天', '秋天', '冬天')
    COLORS = {"春天": color.LIGHT_GREEN, "夏天": color.LIGHT_YELLOW, "秋天": color.LIGHT_ORANGE, "冬天": color.PALE_BLUE}

    def __init__(self, position: tuple[int, int] = (370, 20), font_name: str = "SimSun", font_size: int = 20):
        self.active_time = 0    # 累计活跃时间
        self.last_update_time = pygame.time.get_ticks()   # 上次检查时间

        self.index = 0                           # 当前季节索引
        self.current = self.SEASONS[self.index]  # 当前季节名称
        self.color = self.COLORS[self.current]   # 当前季节颜色
        self.target_color = self.color           # 目标季节颜色

        self.font = get_font(font_name, font_size)
        self.position = position

        self.min_duration = 6000           # 最短降雨时长
        self.max_duration = 20000          # 最长降雨时长
        self.desired_mean = (self.max_duration - self.min_duration) / 4  # 越小越偏短，/4 ~ /3之间
        self.lambda_param = 1 / self.desired_mean
        self.cdf_min = 1 - math.exp(-self.lambda_param * (self.min_duration - self.min_duration))
        self.cdf_max = 1 - math.exp(-self.lambda_param * (self.max_duration - self.min_duration))

        self.rain_check_timer = 0          # 累计降雨检查时间
        self.is_raining = False            # 降雨控制
        self.rain_duration_timer = 0       # 累计降雨时间
        self.rain_duration = self.get_rain_duration()    # 降雨时长

        self.rain_check_interval = 10000   # 每隔 10 秒检查一次是否降雨
        self.raindrops = []                # 雨滴效果

    def update(self, time_speed: int, pause: bool) -> None:
        """根据时间判断是否需要切换季节、是否降雨"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now

        # 即使暂停，颜色渐变和雨滴也可以继续
        self.color = self.lerp_color(self.color, self.target_color, 0.02)
        if self.is_raining:
            self.update_raindrops()

        # 不累计时间，不切换季节或天气
        if pause:
            return

        # 仅在非暂停时累计有效运行时间
        delta_time *= time_speed
        self.active_time += delta_time

        # 更新季节
        if self.active_time > Season.config.switch_interval:
            self.active_time = 0
            self.index = (self.index + 1) % 4
            self.current = self.SEASONS[self.index]
            self.target_color = self.COLORS[self.current]
        
        # 如果当前为非降雨状态
        if not self.is_raining:
            # 增加降雨检查计时器
            self.rain_check_timer += delta_time

            # 超过阈值，则设为 0，并判断是否降雨
            if self.rain_check_timer > self.rain_check_interval:
                self.rain_check_timer = 0
                if random.random() < Season.config.rain_probability:
                    self.start_rain()

        # 如果当前为降雨状态
        else:
            # 增加降雨时长计时器
            self.rain_duration_timer += delta_time

            # 检查是否结束降雨
            if self.rain_duration_timer > self.rain_duration:
                self.stop_rain()

    def start_rain(self) -> None:
        """开始降雨"""
        self.is_raining = True
        self.rain_duration_timer = 0
        self.rain_duration = self.get_rain_duration()
        self.raindrops = [
            {"x": random.randint(0, MapConfig.width), "y": random.randint(-200, 0), "speed": random.randint(5, 12)}
            for _ in range(150)
        ]
        sound_manager.sound_dict['rain'].play(-1)

    def stop_rain(self) -> None:
        """结束降雨"""
        self.is_raining = False
        self.raindrops.clear()
        sound_manager.sound_dict['rain'].stop()

    def update_raindrops(self) -> None:
        """更新雨滴"""
        for drop in self.raindrops:
            drop["y"] += drop["speed"]
            if drop["y"] > MapConfig.height - 100:
                drop["y"] = random.randint(-100, 0)
                drop["x"] = random.randint(0, MapConfig.width)

    def get_rain_duration(self) -> int:
        """计算降雨时长"""
        u = random.random()   # 截断指数分布（inverse transform sampling，限制在 [min, max]）
        u_scaled = u * (self.cdf_max - self.cdf_min) + self.cdf_min   # 生成一个截断后的 CDF 值
        duration = self.min_duration - (1 / self.lambda_param) * math.log(1 - u_scaled)   # 反推对应的 duration
        return int(round(duration / 1000) * 1000)

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制季节和雨滴"""
        text_surface = self.font.render(f"{self.current}", True, (0, 0, 0))
        bg_rect = text_surface.get_rect(topleft=self.position)
        bg_rect.inflate_ip(10, 6)

        # 创建一个支持 alpha 的透明 surface
        tooltip_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        tooltip_surf.fill((255, 255, 255, 140))

        screen.blit(tooltip_surf, bg_rect.topleft)
        screen.blit(text_surface, self.position)

        # 绘制雨滴效果
        if self.is_raining:
            for drop in self.raindrops:
                pygame.draw.line(screen, (100, 100, 255), (drop["x"], drop["y"]), (drop["x"], drop["y"] + 5), 3)

    def change_to(self, target_season: str) -> None:
        """切换季节"""
        self.index = self.SEASONS.index(target_season)
        self.current = target_season
        self.target_color = self.COLORS[target_season]
        self.active_time = 0
        self.last_update_time = pygame.time.get_ticks()

    def get_multiplier_a(self) -> float:
        """获取动物移速倍率"""
        return Season.config.speed_multipliers[self.current]

    def get_multiplier_p(self) -> float:
        """获取植物生长倍率"""
        return Season.config.interval_multipliers[self.current]

    def get_color(self) -> tuple[int, int, int]:
        """获取背景颜色"""
        return self.color
    
    def lerp_color(self, c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        """计算过渡颜色"""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from collections import Counter


    num = 10000
    season = Season()
    rain_durations = []

    for _ in range(num):
        duration = season.get_rain_duration() // 1000
        rain_durations.append(duration)

    # 统计每种秒数的出现次数
    counter = Counter(rain_durations)
    seconds = sorted(counter.keys())
    counts = [counter[sec] for sec in seconds]

    # 绘制柱状图
    plt.figure(figsize=(10, 5))
    plt.bar(seconds, counts, width=0.8, color='skyblue', edgecolor='black')
    plt.title(f'Rain Duration Distribution over {num} samples')
    plt.xlabel('Duration (s)')
    plt.ylabel('Frequency')
    plt.xticks(seconds)  # 逐个显示刻度
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
