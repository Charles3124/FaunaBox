"""
button.py

功能: 游戏 UI 系统
时间: 2025/11/07
版本: 1.0
"""

from __future__ import annotations
from typing import Optional, Callable, TYPE_CHECKING

import pygame

from game.utils import (color, sound_manager, get_font)


if TYPE_CHECKING:
    from game.core import World


class Button:
    """管理按钮的创建、鼠标事件"""
    
    def __init__(
            self, rect_info: tuple[int, int, int, int], on_click: Optional[Callable] = None, text: Optional[str] = None,
            tooltip_text: Optional[str] = None, tooltip_offset: Optional[tuple[int, int]] = None,
            font_size: int = 20, font_name: str = "SimSun", display: bool = True,
            color_idle: tuple[int, int, int] = color.LIGHT_SLATE_GRAY,
            color_hover: tuple[int, int, int] = color.DIM_GRAY,
            text_color: tuple[int, int, int] = color.WHITE
    ):
        self.rect = pygame.Rect(rect_info)      # 创建矩形
        self.display = display                  # 显示状态
        self.text = text                        # 按钮文字
        self.on_click = on_click                # 按钮响应函数

        self.tooltip_offset = tooltip_offset    # 提示框偏移
        self.tooltip_text = tooltip_text        # 提示框文字

        self.alpha = 255                        # 透明度
        self.color_idle = color_idle            # 按钮颜色
        self.color_hover = color_hover          # 悬停颜色
        self.text_color = text_color            # 文字颜色
        self.hovered = False                    # 悬停状态

        self.font = get_font(font_name, font_size)   # 创建字体

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制按钮"""
        if not self.display:
            return

        color_now = self.color_hover if self.hovered else self.color_idle
        text_to_render = self.text() if callable(self.text) else self.text
        text_surface = self.font.render(text_to_render, True, self.text_color)
        text_surface.set_alpha(self.alpha)

        # 创建带透明度的 Surface
        rect_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        # 绘制圆角矩形填充颜色（带透明度）
        pygame.draw.rect(rect_surface, (*color_now, self.alpha), rect_surface.get_rect(), border_radius=8)
        
        # 把透明 surface 贴到屏幕上
        screen.blit(rect_surface, self.rect.topleft)

        # 设置文字透明度
        text_surface.set_alpha(self.alpha)
        screen.blit(
            text_surface,
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2
            )
        )

        # 显示提示框
        if self.hovered and self.tooltip_text:
            self.draw_tooltip(screen)

    def draw_tooltip(self, screen: pygame.surface.Surface) -> None:
        """绘制提示框"""
        tip_surface = self.font.render(self.tooltip_text, True, color.BLACK)
        bg_rect = tip_surface.get_rect()

        # 鼠标当前位置 + 偏移量（避免遮挡）
        mouse_x, mouse_y = pygame.mouse.get_pos()
        offset_x, offset_y = self.tooltip_offset if self.tooltip_offset else (20, 20)
        bg_rect.topleft = (mouse_x + offset_x, mouse_y + offset_y)
        bg_rect.inflate_ip(12, 8)

        # 创建透明白背景（带圆角）
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 140))
        pygame.draw.rect(bg_surface, (255, 255, 255, 140), bg_surface.get_rect(), border_radius=6)

        # 绘制背景与文字
        screen.blit(bg_surface, bg_rect.topleft)
        screen.blit(tip_surface, (bg_rect.left + 6, bg_rect.top + 4))

    def handle_event(self, event: pygame.event.Event) -> None:
        """处理事件"""
        if not self.display:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.on_click is not None:
                sound_manager.sound_dict["click_settings1"].play()
                self.on_click()


def toggle_pause(world: World) -> None:
    """按钮响应函数：暂停"""
    if not world.tech_tree.visible and not world.guide_visible:
        world.pause = not world.pause


def restart(world: World, width: int, height: int, set_buttons: Callable[[list[Button]], None]) -> list[Button]:
    """按钮响应函数：重置"""
    sound_manager.stop_all_bgm()
    sound_manager.play_random_bgm()
    world.restart()
    return create_ui_buttons(world, width, height, set_buttons)


def toggle_tech(world: World) -> None:
    """按钮响应函数：打开科技树"""
    if not world.tech_tree.visible:
        world.last_pause = world.pause
        world.pause = True
    else:
        world.pause = world.last_pause
    world.tech_tree.toggle()


def toggle_guide(world: World) -> None:
    """按钮响应函数：打开指南"""
    if not world.guide_visible:
        world.last_pause_guide = world.pause
        world.pause = True
    else:
        world.pause = world.last_pause_guide
    world.guide_visible = not world.guide_visible


def create_ui_buttons(
        world: World, width: int, height: int, set_buttons: Callable[[list[Button]], None]
) -> list[Button]:
    """创建按钮"""
    return [
        Button(rect_info=(270, 15, 60, 30),
               on_click=lambda: set_buttons(restart(world, width, height, set_buttons)),
               text="重置",
               tooltip_text="重置整个生态箱"),

        Button(rect_info=(190, 15, 60, 30),
               on_click=lambda: toggle_pause(world),
               text="暂停",
               tooltip_text="暂停或继续"),

        Button(rect_info=(130, 15, 45, 30),
               on_click=lambda: world.clock.change_speed(),
               text=lambda: f"{world.clock.speed}x",
               tooltip_text="切换倍速"),

        Button(rect_info=(width - 100, 15, 80, 30),
               on_click=lambda: toggle_tech(world),
               text="科技树",
               tooltip_text="强化你的科技！",
               tooltip_offset=(-150, 0)),

        Button(rect_info=(20, height - 50, 120, 30),
               on_click=world.crafting_system.toggle_visible,
               text="道具制作",
               tooltip_text="制作你的道具！",
               tooltip_offset=(0, -30)),

        Button(rect_info=(width - 100, height - 50, 80, 30),
               on_click=lambda: toggle_guide(world),
               text="指南",
               tooltip_text="查看游戏指南",
               tooltip_offset=(-150, -30)),
    ]
