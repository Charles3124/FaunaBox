# item.py
"""游戏道具系统"""

from __future__ import annotations
from typing import Callable, TYPE_CHECKING

import pygame

from game.entities import Plant
from game.ui import Button
from game.utils import (ITEM_PATH, get_font)


if TYPE_CHECKING:
    from game.core import World


class Item:
    """定义道具属性"""

    def __init__(self, name: str, icon_path: str, cost: dict[str, int], craft_time: int, use_func: Callable[[], None]):
        self.name = name                 # 道具名称
        self.quantity = 0                # 道具数量
        self.icon = pygame.transform.smoothscale(pygame.image.load(icon_path).convert_alpha(), (80, 80))   # 道具贴图
        self.cost = cost                 # 道具消耗
        self.is_crafting = False         # 制作状态
        self.craft_time = craft_time     # 制作时间
        self.use_func = use_func         # 道具效果函数
        self.btn_craft = None            # 道具制作按钮
        self.btn_use = None              # 道具使用按钮


class CraftingSystem:
    """管理道具的生效效果、制作状态及其使用"""

    RESOUCE_NAME = {'leafium': '绿素', 'animite': '兽能', 'ecopoint': '生态点'}

    def __init__(self, world: World, width: int, height: int):
        self.width = width
        self.height = height
        self.visible = False     # 是否展开道具界面
        self.world = world
        self.resource_manager = world.resource_manager

        self.font = get_font("SimSun", 16)
        self.name_font = get_font("SimSun", 16)

        self.items = []                        # 所有道具
        self.buttons = []                      # 所有按钮（仅创建一次）
        self.active_time = {}                  # 每个道具的制造计时
        self.last_update_time = pygame.time.get_ticks()

        self.create_default_items()

        self.current_y = self.height + 100      # 当前绘制 Y 坐标，初始在屏幕底部外
        self.target_y = self.height - 160       # 最终滑动目标位置（即道具栏高度）
        self.slide_speed = 0.15                 # 滑动平滑度（越小越慢）

        self.alpha = 0           # 按钮初始透明度
        self.alpha_target = 255  # 目标透明度
        self.alpha_speed = 10    # 每帧增加透明度值（越大越快）

    def create_default_items(self) -> None:
        """初始化道具、使用逻辑和按钮"""
        def use_heal() -> None:
            """生成治愈性药草"""
            config = self.world.plant_config
            config.is_medicative = True
            Plant.states["is_medicative"] += config.medicative_duration

        def use_speed() -> None:
            """给鳄鱼加速"""
            config = self.world.croc_config
            config.boosting = True
            for croc in self.world.crocodiles:
                croc.boost_active_time += config.boost_duration

        def use_rain() -> None:
            """立刻降雨"""
            self.world.season.start_rain()

        def use_invincible() -> None:
            """植物护盾"""
            config = self.world.plant_config
            config.is_invincible = True
            Plant.states["is_invincible"] += config.invincible_duration

        # 添加道具
        self.items.append(Item("治愈药草", ITEM_PATH / 'heal.png', {'leafium': 10}, 10000, use_heal))
        self.items.append(Item("加速鳄鱼", ITEM_PATH / 'croc.png', {'animite': 10}, 10000, use_speed))
        self.items.append(Item("人工降雨", ITEM_PATH / 'rain.png', {'ecopoint': 10}, 10000, use_rain))
        self.items.append(Item("植物护盾", ITEM_PATH / 'invincible.png', {'leafium': 10}, 10000, use_invincible))

        # 为每个道具分配两个按钮（制作 + 使用）
        x_start = 160
        y_start = self.height - 160
        box_size = 150
        padding = 20

        for idx, item in enumerate(self.items):
            x = x_start + idx * (box_size + padding)
            y = y_start

            # 创建制作按钮
            item.btn_craft = Button((x + 10, y + 115, 60, 28), text="制作", on_click=lambda i=item: self.try_craft(i),
                                    color_idle=(100, 180, 100), color_hover=(70, 160, 70), font_size=18)

            # 创建使用按钮
            item.btn_use = Button((x + 80, y + 115, 60, 28), text="使用", on_click=lambda i=item: self.try_use(i),
                                  color_idle=(180, 100, 100), color_hover=(160, 70, 70), font_size=18)

            # 加入按钮管理列表
            self.buttons.extend([item.btn_craft, item.btn_use])
            self.active_time[item.name] = 0

    def toggle_visible(self) -> None:
        """展开或收起道具面板"""
        self.visible = not self.visible
        if self.visible:
            self.current_y = self.height + 100
            self.alpha = 0

    def try_craft(self, item: Item) -> None:
        """尝试制造道具：资源检查、计时开始"""
        if item.is_crafting:
            return
        for k, v in item.cost.items():
            if getattr(self.resource_manager, k) < v:
                return
        for k, v in item.cost.items():
            setattr(self.resource_manager, k, getattr(self.resource_manager, k) - v)
        item.is_crafting = True

    def try_use(self, item: Item) -> None:
        """使用道具，触发效果"""
        if item.quantity > 0:
            item.use_func()
            item.quantity -= 1

    def update(self, time_speed: int, pause: bool) -> None:
        """更新道具制造进度"""
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now
        if pause:
            return

        delta_time *= time_speed

        for item in self.items:
            if item.is_crafting:
                self.active_time[item.name] += delta_time
                if self.active_time[item.name] > item.craft_time:
                    self.active_time[item.name] = 0
                    item.is_crafting = False
                    item.quantity += 1

    def draw(self, screen: pygame.Surface) -> None:
        """绘制道具界面，包括图标、文字、进度条和按钮"""        
        self.draw_active_icons(screen)

        if not self.visible:
            return

        # 插值逼近目标位置
        self.current_y += (self.target_y - self.current_y) * self.slide_speed
        if abs(self.current_y - self.target_y) < 1:
            self.current_y = self.target_y

        # 更新按钮透明度
        if self.alpha < self.alpha_target:
            self.alpha = min(self.alpha + self.alpha_speed, self.alpha_target)

        x_start = 160
        y_start = int(self.current_y)
        box_size = 150
        padding = 20

        for idx, item in enumerate(self.items):
            x = x_start + idx * (box_size + padding)
            y = y_start

            # 背景框（带透明度）
            bg_surface = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
            bg_surface.fill((240, 240, 240, 140))
            screen.blit(bg_surface, (x, y))
            pygame.draw.rect(screen, (112, 128, 144), (x, y, box_size, box_size), 2)

            # 图标
            screen.blit(item.icon, (x + (box_size - 80) // 2, y + 5))

            # 药水名称（竖排渲染）
            name_x = x + 115
            name_y = y + 10
            for ch in item.name:
                ch_surface = self.name_font.render(ch, True, (50, 50, 50))
                screen.blit(ch_surface, (name_x, name_y))
                name_y += ch_surface.get_height() + 1  # 行间距可调

            # 数量
            qty_surface = self.font.render(f"x{item.quantity}", True, (0, 0, 0))
            screen.blit(qty_surface, (x + 10, y + 10))

            # 资源消耗
            cost_text = ", ".join([f"{self.RESOUCE_NAME[k]}:{v}" for k, v in item.cost.items()])
            cost_surface = self.font.render(cost_text, True, (100, 50, 50))
            screen.blit(cost_surface, (x + 10, y + 82))

            # 制作进度条与剩余时间
            if item.is_crafting:
                remaining_time = item.craft_time - self.active_time[item.name]

                bar_w = int((1 - remaining_time / item.craft_time) * (box_size - 20))
                pygame.draw.rect(screen, (100, 200, 100), (x + 10, y + 105, bar_w, 5))

                time_left = remaining_time // 1000 + 1
                time_surface = self.font.render(f"{time_left}s", True, (150, 0, 0))
                screen.blit(time_surface, (x + box_size - 40, y + 82))

            # 按钮绘制
            item.btn_craft.alpha = self.alpha
            item.btn_use.alpha = self.alpha
            item.btn_craft.draw(screen)
            item.btn_use.draw(screen)

    def draw_active_icons(self, screen: pygame.surface.Surface) -> None:
        """绘制生效的道具"""
        active_icons = []

        if self.world.plant_config.is_medicative:
            active_icons.append(self.items[0].icon)  # 治愈药草

        if self.world.croc_config.boosting:
            active_icons.append(self.items[1].icon)  # 加速鳄鱼

        if self.world.plant_config.is_invincible:
            active_icons.append(self.items[3].icon)  # 植物护盾

        icon_size = 32
        padding = 5
        start_x = self.width - (icon_size + padding) * len(active_icons) - 10
        y = 50

        for i, icon in enumerate(active_icons):
            icon_small = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            screen.blit(icon_small, (start_x + i * (icon_size + padding), y))

    def handle_event(self, event: pygame.event.Event) -> None:
        """转发事件给所有按钮"""
        if not self.visible:
            return
        for btn in self.buttons:
            btn.handle_event(event)
