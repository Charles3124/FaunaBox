# world.py
"""游戏世界管理核心类"""

import pygame

from game.core import (Clock, ResourceManager)
from game.utils import (RabbitConfig, CrocodileConfig, PlantConfig, SeasonConfig, draw_guide)
from game.environment import (Season, DisasterManager)
from game.systems import (CraftingSystem, TechTree)
from game.entities import (Plant, Rabbit, Crocodile, Animal)


class World:
    """创建和管理游戏中的所有实体和系统"""

    def __init__(self, width: int, height: int, test_state: int = 0, initial_speed: int = 1, speeds: list[int] = [1, 2, 4]):
        # 基础状态
        self.width = width
        self.height = height
        self.pause = False
        self.end = False
        self.ending1 = False
        self.ending2 = False
        self.ending3 = False

        self.last_pause = None
        self.guide_visible = False
        self.last_pause_guide = None

        # 配置和系统初始化（时间、季节、灾害、资源）
        self.clock = Clock(initial_speed, speeds)
        self.season_config = SeasonConfig()
        Season.config = self.season_config
        self.season = Season()
        self.disaster = DisasterManager()
        self.resource_manager = ResourceManager(test=test_state)

        # 配置和实体（兔子、鳄鱼、植物）
        self.dead_animals = []

        self.rabbit_config = RabbitConfig()
        Rabbit.config = self.rabbit_config
        self.rabbits = Rabbit.initialize_animals(self.rabbit_config)

        self.croc_config = CrocodileConfig()
        Crocodile.config = self.croc_config
        self.crocodiles = Crocodile.initialize_animals(self.croc_config)

        self.plant_config = PlantConfig()
        Plant.config = self.plant_config
        self.plants = Plant.initialize_plants(self.plant_config.initial_num)

        # 科技树和道具系统
        self.tech_tree = TechTree(self.resource_manager, self.width, self.height)
        self.crafting_system = CraftingSystem(self, self.width, self.height)

    @property
    def animals(self) -> list[Animal]:
        """获取所有动物"""
        return self.rabbits + self.crocodiles

    def can_update(self) -> bool:
        """检测是否结束"""
        return not self.end

    def can_progress(self) -> bool:
        """检测是否暂停"""
        return not self.pause and not self.end

    def update_always(self) -> None:
        """始终更新"""
        self.resource_manager.update_ecopoints(self.clock.speed, self.pause)
        Plant.add_new_plant(self.plants, self.season, self.resource_manager, self.clock.speed, self.pause)
        self.season.update(self.clock.speed, self.pause)
        self.clock.update(self.pause)
        self.disaster.update(self, self.season, self.clock.speed, self.pause)
        self.crafting_system.update(self.clock.speed, self.pause)

        for animal in self.animals:
            animal.move(
                self.crocodiles, self.rabbits, self.dead_animals,
                self.plants, self.plant_config,
                self.season, self.clock.speed, self.pause
            )

        Plant.remove_plants_near_animals(
            self.plants, self.rabbits,
            self.season, self.resource_manager, self.clock.speed, self.pause
        )

    def update_when_active(self) -> None:
        """非暂停时更新"""
        self.rabbits.extend(Rabbit.add_new_animal(
            self.rabbits, self.rabbit_config, self.animals,
            self.resource_manager, self.season
        ))
        
        self.crocodiles.extend(Crocodile.add_new_animal(
            self.crocodiles, self.croc_config, self.animals,
            self.resource_manager, self.season
        ))

        self.rabbits = Rabbit.remove_old_animals(self.rabbits)
        self.crocodiles = Crocodile.remove_old_animals(self.crocodiles)

        for dead in self.dead_animals:
            if isinstance(dead, Rabbit) and dead in self.rabbits:
                self.rabbits.remove(dead)
        self.dead_animals.clear()

    def check_end(self) -> None:
        """检测结束状态"""
        if len(self.plants) == 0:
            self.end = self.ending1 = True
        elif len(self.rabbits) == 0:
            self.end = self.ending2 = True
        elif len(self.crocodiles) == 0:
            self.end = self.ending3 = True

    def restart(self) -> None:
        """重置世界"""
        self.__init__(self.width, self.height)

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制世界"""
        # 绘制建筑、植物、动物
        if not self.tech_tree.visible:
            for building in self.tech_tree.buildings.values():
                building.draw(screen)
            for plant in self.plants:
                plant.draw(screen)
            for animal in self.animals:
                animal.draw(screen)

        # 绘制科技树、季节、状态、时间、资源、道具
        self.tech_tree.draw(screen)
        self.season.draw(screen)
        self.clock.draw(screen)
        self.resource_manager.draw(screen)
        self.disaster.draw(screen, self.clock.speed, self.pause)
        self.crafting_system.draw(screen)

        if self.guide_visible:
            draw_guide(screen)
