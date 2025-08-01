# main.py
import pygame
from game.utils.helpers import draw_centered_text
from game.utils.config import MapConfig
from game.core.world import World
from game.core.sounds import sound_manager
from game.ui.button import Button

# ---------- 初始化 ----------
pygame.init()
screen = pygame.display.set_mode((MapConfig.width, MapConfig.height))
pygame.display.set_caption("生态箱")
world = World(MapConfig.width, MapConfig.height, test_state=1)

# ---------- 辅助函数 ----------
def toggle_pause():
    """按钮响应函数：暂停"""
    if not world.tech_tree.visible and not world.guide_visible:
        world.pause = not world.pause

def restart():
    """按钮响应函数：重置"""
    sound_manager.stop_all_bgm()
    sound_manager.play_random_bgm()
    world.restart()
    create_buttons()

def toggle_tech():
    """按钮响应函数：打开科技树"""
    if not world.tech_tree.visible:
        world.last_pause = world.pause
        world.pause = True
    else:
        world.pause = world.last_pause
    world.tech_tree.toggle()

def toggle_guide():
    """按钮响应函数：打开指南"""
    if not world.guide_visible:
        world.last_pause_guide = world.pause
        world.pause = True
    else:
        world.pause = world.last_pause_guide
    world.guide_visible = not world.guide_visible

def try_consume(resource_type, cost):
    """判断资源是否足够"""
    current = getattr(world.resource_manager, resource_type)
    if current >= cost:
        setattr(world.resource_manager, resource_type, current - cost)
        return True
    return False

def create_buttons():
    """创建按钮"""
    global buttons
    buttons = [
        Button((270, 15, 60, 30), on_click=restart, text="重置",
               tooltip_text="重置整个生态箱"),

        Button((190, 15, 60, 30), on_click=toggle_pause, text="暂停",
               tooltip_text="暂停或继续"),

        Button((130, 15, 45, 30), on_click=lambda: world.clock.change_speed(), text=lambda: f"{world.clock.speed}x",
               tooltip_text="切换倍速"),

        Button((MapConfig.width - 100, 15, 80, 30), on_click=toggle_tech, text="科技树",
               tooltip_text="强化你的科技！", tooltip_offset=(-150, 0)),

        Button((20, MapConfig.height - 50, 120, 30), on_click=world.crafting_system.toggle_visible, text="道具制作",
               tooltip_text="制作你的道具！", tooltip_offset=(0, -30)),

        Button((MapConfig.width - 100, MapConfig.height - 50, 80, 30), on_click=toggle_guide, text="指南",
               tooltip_text="查看游戏指南", tooltip_offset=(-150, -30))

    ]

# ---------- 创建按钮 ----------
buttons = []
create_buttons()

# ---------- 主循环 ----------
running = True
sound_manager.play_random_bgm()
while running:
    # 绘制背景颜色
    screen.fill(world.season.get_color())

    # 动物和植物灭绝检测
    world.check_end()

    # 事件监听
    for event in pygame.event.get():
        # 处理退出游戏指令
        if event.type == pygame.QUIT:
            running = False

        # 处理所有按钮点击事件
        for b in buttons:
            b.handle_event(event)
        
        world.crafting_system.handle_event(event)

        # 科技树打开时，处理科技树点击事件
        if world.tech_tree.visible and event.type == pygame.MOUSEBUTTONDOWN:
            world.tech_tree.handle_click(event.pos)

        # 处理键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                restart()
            elif event.key == pygame.K_TAB:
                world.clock.change_speed()
            elif event.key in (pygame.K_p, pygame.K_SPACE):
                toggle_pause()

    # 更新逻辑
    if world.can_update():
        world.update_always()
        if world.can_progress():
            world.update_when_active()
    
    # 绘制世界
    world.draw(screen)

    # 绘制按钮
    for b in buttons:
        b.draw(screen)

    # 显示结局
    if world.ending1:
        draw_centered_text(screen, world.clock, "植物灭绝了！", y_offset=-20)
    elif world.ending2:
        draw_centered_text(screen, world.clock, "兔子灭绝了！", y_offset=-20)
    elif world.ending3:
        draw_centered_text(screen, world.clock, "鳄鱼灭绝了！", y_offset=-20)

    # 更新一帧画面
    pygame.display.flip()
    pygame.time.Clock().tick(60)

sound_manager.stop_all_bgm()
pygame.quit()
