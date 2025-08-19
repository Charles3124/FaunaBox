# tech_tree.py
"""游戏科技树系统"""

import pygame

from game.core import ResourceManager
from game.utils import (BUILDING_PATH, color, sound_manager, get_font)
from game.entities import (Rabbit, Crocodile, Plant, Building)
from game.environment import Season


class TechTree:
    """管理科技树的生效效果、生效状态"""

    RESOUCE_NAME = {'leafium': '绿素', 'animite': '兽能', 'ecopoint': '生态点'}

    def __init__(self, resource_manager: ResourceManager, width: int, height: int, font_name: str = "SimSun", font_size: int = 20):
        self.resource_manager = resource_manager   # 资源管理器
        self.width = width             # 屏幕宽度
        self.height = height           # 屏幕高度
        self.font = get_font(font_name, font_size)   # 创建字体
        self.visible = False           # 可见性
        self.unlock_message = None     # 解锁提示文字
        self.unlock_time = 0           # 解锁时间
        self.message_duration = 2000   # 文字显示时长

        self.hovered_index = None                  # 悬停位置
        self.color_idle = color.LIGHT_GREY         # 默认颜色
        self.color_hover = color.VERY_LIGHT_GREY   # 悬停颜色
        self.color_unlocked = color.GREEN          # 已解锁颜色

        # 区域和科技内容
        self.techs = {
            "植物效果": [
                {"name": "繁殖加速-α型", "cost": {"leafium": 20}, "unlocked": False, "applied": False},
                {"name": "繁殖加速-β型", "cost": {"leafium": 20}, "unlocked": False, "applied": False},
                {"name": "亲水基因", "cost": {"leafium": 30}, "unlocked": False, "applied": False},
                {"name": "耐寒基因", "cost": {"leafium": 60}, "unlocked": False, "applied": False},
            ],
            "动物效果": [
                {"name": "兔子：速度增强", "cost": {"animite": 20}, "unlocked": False, "applied": False},
                {"name": "兔子：繁殖季", "cost": {"animite": 20}, "unlocked": False, "applied": False},
                {"name": "鳄鱼：节育本能", "cost": {"animite": 20}, "unlocked": False, "applied": False},
                {"name": "鳄鱼：咬合进化", "cost": {"animite": 20}, "unlocked": False, "applied": False},
            ],
            "天气效果": [
                {"name": "生态调节系统", "cost": {"ecopoint": 10}, "unlocked": False, "applied": False},
                {"name": "季节稳定系统", "cost": {"ecopoint": 20}, "unlocked": False, "applied": False},
                {"name": "降雨干预系统", "cost": {"ecopoint": 20}, "unlocked": False, "applied": False},
            ],
            "建筑效果": [
                {"name": "植物庇护站", "cost": {"leafium": 15, "ecopoint": 10}, "unlocked": False, "applied": False},
                {"name": "动物缓冲地带", "cost": {"animite": 15, "ecopoint": 10}, "unlocked": False, "applied": False},
                {"name": "兔子哨站", "cost": {"animite": 15, "ecopoint": 10}, "unlocked": False, "applied": False},
            ]
        }

        self.tooltips = {
            "繁殖加速-α型": "略微提高植物的繁殖速度",
            "繁殖加速-β型": "植物每次有概率双倍繁殖",
            "亲水基因": "植物在下雨时繁殖更快，但冬天更容易死亡",
            "耐寒基因": "植物在冬天不再因严寒而死亡",

            "兔子：速度增强": "兔子速度更快，但觅食范围略微缩小",
            "兔子：繁殖季": "春天兔子繁殖更快",
            "鳄鱼：节育本能": "鳄鱼需要多吃一只兔子才能繁殖",
            "鳄鱼：咬合进化": "鳄鱼的捕食范围变大",

            "生态调节系统": "生态点增长得更快",
            "季节稳定系统": "增长每个季节的时长",
            "降雨干预系统": "全年降雨增多",

            "植物庇护站": "略微提高冬天植物的繁殖速度",
            "动物缓冲地带": "略微提高冬天所有动物的移动速度",
            "兔子哨站": "扩大兔子感知掠食者的范围",
        }

        self.rects = []  # 存储按钮区域（供点击判定）

        self.buildings = {
            "植物庇护站": Building("植物庇护站", BUILDING_PATH / 'plant_shelter.png', (200, 200), (200, 200)),
            "动物缓冲地带": Building("动物缓冲地带", BUILDING_PATH / 'animal_zone.png', (width - 200, height - 300), (200, 200)),
            "兔子哨站": Building("兔子哨站", BUILDING_PATH / 'rabbit_outpost.png', (200, height - 200), (200, 200)),
        }

    def toggle(self) -> None:
        """切换可见性"""
        self.visible = not self.visible
        if self.visible:   # 切换 BGM
            sound_manager.stop_all_bgm()
        else:
            sound_manager.play_random_bgm()

    def handle_click(self, pos: tuple[int, int]) -> None:
        """处理点击事件"""
        if not self.visible:
            return
        for rect, area, index in self.rects:
            if rect.collidepoint(pos):
                tech = self.techs[area][index]
                if not tech["unlocked"] and self.can_afford(tech["cost"]):
                    self.unlock_tech(area, index)

    def can_afford(self, cost: dict[str, int]) -> bool:
        """判断资源是否足够点亮科技"""
        return all(getattr(self.resource_manager, key) >= value for key, value in cost.items())

    def unlock_tech(self, area: str, index: int) -> None:
        """解锁科技，并应用科技效果"""
        tech = self.techs[area][index]
        for key, value in tech["cost"].items():
            setattr(self.resource_manager, key, getattr(self.resource_manager, key) - value)
        tech["unlocked"] = True
        self.apply_effects()
        self.unlock_message = f"科技已解锁：{tech['name']}！"  # 解锁提示
        self.unlock_time = pygame.time.get_ticks()

    def apply_effects(self) -> None:
        """根据已解锁科技，修改系统配置"""
        for area, techs in self.techs.items():
            for i, tech in enumerate(techs):
                if tech['unlocked'] and not tech['applied']:
                    sound_manager.sound_dict['click_tech'].play()
                    name = tech['name']

                    # 植物科技
                    if name == '繁殖加速-α型':    # 繁殖加速-α型：略微提高植物的繁殖速度
                        Plant.config.reproduction_interval -= 500
                    elif name == '繁殖加速-β型':  # 繁殖加速-β型：植物每次有概率双倍繁殖
                        Plant.config.double_reproduction = True
                    elif name == '亲水基因':      # 亲水基因：植物在下雨时繁殖更快，但冬天更容易死亡
                        Plant.config.rain_bonus = 0.5
                        Plant.config.winter_harshness = 1.5
                    elif name == '耐寒基因':      # 耐寒基因：植物在冬天不再因严寒而死亡
                        Plant.config.survive_winter = True

                    # 动物科技
                    elif name == '兔子：速度增强':  # 兔子：速度增强：兔子速度更快，但觅食范围略微缩小
                        Rabbit.config.ave_speed += 0.2
                        Rabbit.config.min_plant_distance -= 10
                    elif name == '兔子：繁殖季':    # 兔子：繁殖季：春天兔子繁殖更快
                        Rabbit.config.reproduction_threshold['春天'] -= 1
                    elif name == '鳄鱼：节育本能':  # 鳄鱼：节育本能：鳄鱼需要多吃一只兔子才能繁殖
                        for s in ('春天', '夏天', '秋天', '冬天'):
                            Crocodile.config.reproduction_threshold[s] += 1
                    elif name == '鳄鱼：咬合进化':  # 鳄鱼：咬合进化：鳄鱼的捕食范围变大
                        Crocodile.config.min_eat_distance += 10

                    # 天气科技
                    elif name == '生态调节系统':  # 生态调节系统：生态点增长得更快
                        ResourceManager.eco_interval -= 3000
                    elif name == '季节稳定系统':  # 季节稳定系统：每个季节延长 5 秒
                        Season.config.switch_interval += 5000
                    elif name == '降雨干预系统':  # 降雨干预系统：全年降雨增多
                        Season.config.rain_probability = 0.4

                    # 建筑科技
                    elif name == '植物庇护站':  # 植物庇护站：植物在冬天的繁殖速度更快
                        Season.config.interval_multipliers['冬天'] = 1.5
                        self.buildings[name].visible = True
                    elif name == '动物缓冲地带':  # 动物缓冲地带：动物在冬天的移速略微增加
                        Season.config.speed_multipliers['冬天'] = 0.8
                        self.buildings[name].visible = True
                    elif name == '兔子哨站':    # 兔子哨站：扩大兔子感知掠食者的范围
                        Rabbit.config.min_croc_distance += 50
                        self.buildings[name].visible = True
                    
                    tech["applied"] = True  # 标记为已应用

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制科技树、说明和提示"""
        if not self.visible:
            return

        # 更新悬停状态
        self.update_hover_state()

        # 科技方框布局参数
        margin_x = 80
        margin_y = 150
        spacing_y = 60
        box_height = 40
        padding_x = 20   # 水平方向的内边距
        self.rects = []

        # 区域布局
        positions = {
            "植物效果": (margin_x, margin_y),
            "动物效果": (self.width // 2 + margin_x, margin_y),
            "天气效果": (margin_x, self.height // 2 + margin_y - 80),
            "建筑效果": (self.width // 2 + margin_x, self.height // 2 + margin_y - 80),
        }

        for area, techs in self.techs.items():
            base_x, base_y = positions[area]
            label = self.font.render(area, True, color.BLACK)
            screen.blit(label, (base_x, base_y - 40))

            for i, tech in enumerate(techs):
                # 拼接科技名和消耗文本
                tech_text = f"{tech['name']} - " + ", ".join([f"{self.RESOUCE_NAME[k]}：{v}" for k, v in tech['cost'].items()])
                text_surface = self.font.render(tech_text, True, (0, 0, 0))

                # 动态获取文本宽度
                text_width, _ = self.font.size(tech_text)
                box_width = text_width + padding_x * 2

                # 绘制背景框
                rect = pygame.Rect(base_x, base_y + i * spacing_y, box_width, box_height)

                if tech['unlocked']:
                    cur_color = self.color_unlocked
                elif self.hovered_index == (area, i):
                    cur_color = self.color_hover
                else:
                    cur_color = self.color_idle

                pygame.draw.rect(screen, cur_color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

                # 绘制文字
                screen.blit(text_surface, (rect.x + padding_x, rect.y + 8))

                # 保存点击区域
                self.rects.append((rect, area, i))
        
        # 绘制悬停说明
        self.draw_hover_description(screen)

        # 绘制解锁提示
        if self.unlock_message and pygame.time.get_ticks() - self.unlock_time < self.message_duration:
            tip_surface = self.font.render(self.unlock_message, True, color.BLACK)
            bg_rect = tip_surface.get_rect(topright=(self.width - 30, 60))
            bg_rect.inflate_ip(12, 6)

            # 白色半透明背景
            tip_bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            tip_bg.fill((255, 255, 255, 140))
            screen.blit(tip_bg, bg_rect.topleft)

            # 文字绘制
            screen.blit(tip_surface, (bg_rect.left + 6, bg_rect.top + 3))

    def draw_hover_description(self, screen: pygame.surface.Surface) -> None:
        """绘制悬停说明"""
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        for rect, area, index in self.rects:
            if rect.collidepoint(mouse_pos):
                tech = self.techs[area][index]
                desc = self.tooltips.get(tech['name'], "")
                if desc:
                    # 渲染文本
                    text_surf = self.font.render(desc, True, (0, 0, 0))
                    padding = 10
                    bg_rect = text_surf.get_rect()
                    bg_rect.topleft = (mouse_pos[0] + 20, mouse_pos[1] + 20)
                    bg_rect.inflate_ip(padding * 2, padding * 2)

                    # 绘制背景框
                    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                    bg_surf.fill((255, 255, 255, 140))
                    screen.blit(bg_surf, bg_rect.topleft)

                    # 绘制说明文字
                    screen.blit(text_surf, (bg_rect.x + padding, bg_rect.y + padding))
                break

    def update_hover_state(self) -> None:
        """更新按钮悬停状态"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_index = None
        
        for rect, area, index in self.rects:
            if rect.collidepoint(mouse_pos):
                self.hovered_index = (area, index)
                break
