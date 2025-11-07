"""
main.py

功能: 主函数，通过 World 类管理整个游戏
时间: 2025/11/07
版本: 1.0
"""

import pygame

from game.core import World
from game.utils import (MapConfig, draw_centered_text, sound_manager)
from game.ui import (Button, create_ui_buttons, toggle_pause, restart)


# ---------- 初始化 ----------
pygame.init()
WIDTH, HEIGHT = MapConfig.width, MapConfig.height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("生态箱")

# 创建世界和 UI 按钮
world = World(WIDTH, HEIGHT, test_state=1)

def set_buttons(new_buttons: list[Button]) -> None:
    """创建 UI 按钮"""
    global buttons
    buttons = new_buttons

buttons: list[Button] = create_ui_buttons(world, WIDTH, HEIGHT, set_buttons)


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
                set_buttons(restart(world, WIDTH, HEIGHT, set_buttons))
            elif event.key == pygame.K_TAB:
                world.clock.change_speed()
            elif event.key in (pygame.K_p, pygame.K_SPACE):
                toggle_pause(world)

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
        draw_centered_text(screen, world.clock, text="植物灭绝了！")
    elif world.ending2:
        draw_centered_text(screen, world.clock, text="兔子灭绝了！")
    elif world.ending3:
        draw_centered_text(screen, world.clock, text="鳄鱼灭绝了！")

    # 更新一帧画面
    pygame.display.flip()
    pygame.time.Clock().tick(60)


# ---------- 结束游戏 ----------
sound_manager.stop_all_bgm()
pygame.quit()
