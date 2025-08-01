# button.py
import pygame
from ..utils import color
from ..core.sounds import sound_manager

class Button:
    
    def __init__(self, rect_or_center, on_click=None, text=None, tooltip_text=None, tooltip_offset=None,
                 font_size=20, font_name="SimSun", display=True,
                 color_idle=color.LIGHT_SLATE_GRAY, color_hover=color.DIM_GRAY, text_color=color.WHITE):
        self.rect = pygame.Rect(rect_or_center) # 创建矩形
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

        self.font = pygame.font.SysFont(font_name, font_size)   # 创建字体

    def draw(self, screen):
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
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2, self.rect.centery - text_surface.get_height() // 2))

        # 显示提示框
        if self.hovered and self.tooltip_text:
            self.draw_tooltip(screen)

    def draw_tooltip(self, screen):
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

    def handle_event(self, event):
        """处理事件"""
        if not self.display:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.on_click is not None:
                sound_manager.sound_dict['click_settings1'].play()
                self.on_click()
