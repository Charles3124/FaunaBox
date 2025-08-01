# utils.py
import pygame
from . import color
from .config import MapConfig

pygame.font.init()

def draw_centered_text(screen, clock, text, y_offset=0, text_color=color.BLACK, font_size=32, font_name="SimSun"):
    """绘制游戏结局"""
    font = pygame.font.SysFont(font_name, 32)
    text_surface = font.render(text, True, text_color)

    x = (MapConfig.width - text_surface.get_width()) // 2
    y = (MapConfig.height - text_surface.get_height()) // 2 + y_offset

    screen.blit(text_surface, (x, y))

    font = pygame.font.SysFont(font_name, 22)
    text_surface = font.render(f'生态箱持续到了 {clock.years} 年 {clock.months} 月', True, text_color)

    x = (MapConfig.width - text_surface.get_width()) // 2
    y = (MapConfig.height - text_surface.get_height()) // 2 + y_offset + 60

    screen.blit(text_surface, (x, y))

def draw_guide(screen, world):
    """绘制指南界面"""
    # 半透明背景覆盖
    overlay = pygame.Surface((MapConfig.width, MapConfig.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 黑色半透明
    screen.blit(overlay, (0, 0))
    
    # 绘制指南窗口
    guide_width, guide_height = 550, 550
    guide_rect = pygame.Rect((MapConfig.width - guide_width) // 2, 130, guide_width, guide_height)
    pygame.draw.rect(screen, color.WHITE, guide_rect, border_radius=10)
    pygame.draw.rect(screen, color.BLACK, guide_rect, 2, border_radius=10)
    
    # 保存指南矩形位置供事件处理使用
    world.guide_rect = guide_rect
    
    # 标题
    title_font = pygame.font.SysFont("SimHei", 30)
    title = title_font.render("游戏指南", True, color.BLACK)
    screen.blit(title, (guide_rect.centerx - title.get_width() // 2, guide_rect.top + 20))
    
    # 内容
    content_font = pygame.font.SysFont("SimSun", 18)
    guide_text = [
        "",
        "欢迎来到生态箱游戏！这是一个模拟生态系统的游戏，",
        "包含植物、兔子和鳄鱼，形成了简易的食物链。",
        "",
        "游戏说明：",
        "1. 食物链：植物 → 兔子 → 鳄鱼",
        "2. 科技树：解锁各种强化功能",
        "3. 道具：制作有用的道具影响生态系统",
        "4. 资源：积累和使用资源",
        "5. 季节和天气：影响生物行为",
        "6. 灾难事件：随机发生的挑战",
        "",
        "操作指南：",
        "- 暂停/继续：空格键 / P键 / 暂停按钮",
        "- 重置游戏：R键 / 重置按钮",
        "- 加速游戏：Tab键 / 倍速按钮",
        "",
        "游戏目标：",
        "保持生态平衡，防止所有物种灭绝！"
    ]
    
    # 渲染文本
    y_pos = guide_rect.top + 60
    for line in guide_text:
        text_surface = content_font.render(line, True, color.BLACK)
        screen.blit(text_surface, (guide_rect.left + 20, y_pos))
        y_pos += 25
