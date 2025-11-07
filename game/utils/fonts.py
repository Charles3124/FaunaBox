# fonts.py
"""游戏字体系统"""

import pygame


class FontManager:
    """创建并缓存字体"""
    
    def __init__(self):
        self.font_cache = {}
        
    def get_font(self, name: str = 'SimSun', size: int = 24, bold: bool = False) -> pygame.font.Font:
        """获取字体对象"""
        # 创建缓存的键
        cache_key = (name, size, bold)
        
        # 如果字体已经在缓存中，直接返回
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # 创建新字体并缓存
        font = pygame.font.SysFont(name, size, bold)
        self.font_cache[cache_key] = font
        return font


# 创建全局字体管理器实例
font_manager = FontManager()

# 快捷访问函数
def get_font(name: str = 'SimSun', size: int = 24, bold: bool = False) -> pygame.font.Font:
    """快捷获取字体对象的函数"""
    return font_manager.get_font(name, size, bold)
