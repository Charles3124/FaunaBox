# plant.py
from __future__ import annotations
import pygame
import random
from game.utils import (MapConfig, PlantConfig)
from game.core import ResourceManager
from game.environment import Season

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.entities import Rabbit

class Plant:
    config = None
    active_time = 0
    boost_active_time = 0
    medicative_active_time = 0
    invincible_active_time = 0
    last_update_time = pygame.time.get_ticks()
    last_remove_time = pygame.time.get_ticks()
    loaded_images = {}
    
    def __init__(self, x: float, y: float, config: PlantConfig):
        self.x = x
        self.y = y
        self.size = config.size

        if config.image not in Plant.loaded_images:
            Plant.loaded_images[config.image] = pygame.transform.smoothscale(pygame.image.load(config.image).convert_alpha(),
                                                                             (self.size[0] * 2, self.size[1] * 2))
        self.image = Plant.loaded_images[config.image]

        self.medicative = False   # 是否有治愈性

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制植物"""
        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)

    @staticmethod
    def is_too_close_p(new_plant: Plant, plants: list[Plant]) -> bool:
        """控制植物距离"""
        for plant in plants:
            distance = ((new_plant.x - plant.x) ** 2 + (new_plant.y - plant.y) ** 2) ** 0.5
            if distance < Plant.config.min_distance:
                return True
        return False

    @staticmethod
    def create_new_p(config: PlantConfig) -> tuple[float, float]:
        new_x = random.uniform(config.size[0], MapConfig.width - config.size[0])
        new_y = random.uniform(config.size[1], MapConfig.height - config.size[1])
        return Plant(new_x, new_y, config)

    @classmethod
    def initialize_plants(cls, num_plants: int) -> list[Plant]:
        """初始化植物"""
        plants = []
        for _ in range(num_plants):
            for _ in range(100):
                new_plant = cls.create_new_p(cls.config)
                if not cls.is_too_close_p(new_plant, plants):
                    plants.append(new_plant)
                    break
        return plants

    @classmethod
    def add_one_plant(cls, plants: list[Plant]) -> Plant:
        """加一个植物"""
        for _ in range(100):
            new_plant = cls.create_new_p(cls.config)
            if not cls.is_too_close_p(new_plant, plants):
                break
        return new_plant

    @classmethod
    def add_new_plant(cls, plants: list[Plant], season: Season, resource_manager: ResourceManager,
                      time_speed: int, pause: bool) -> None:
        """植物繁殖"""
        # 如果还有植物，则植物可以繁衍
        if len(plants) != 0:
            # 活跃时间检查
            now = pygame.time.get_ticks()
            delta_time = now - cls.last_update_time
            cls.last_update_time = now
            if pause:
                return
            delta_time *= time_speed
            cls.active_time += delta_time

            # 计算季节倍率
            base_interval = cls.config.reproduction_interval
            base_interval *= season.get_multiplier_p()

            # 判断是否在下雨
            if season.is_raining:
                base_interval *= cls.config.rain_bonus

            # 判断是否处于加速状态
            if cls.config.boosting and cls.boost_active_time > 0:
                cls.boost_active_time -= delta_time
                interval = base_interval * cls.config.boost_rate   # 加速生长
            else:
                cls.boost_active_time = 0
                cls.config.boosting = False
                interval = base_interval   # 如果超时，关闭加速

            # 判断是否拥有治愈能力
            if cls.config.is_medicative and cls.medicative_active_time > 0:
                cls.medicative_active_time -= delta_time
            else:
                cls.medicative_active_time = 0
                cls.config.is_medicative = False   # 关闭治愈能力

            # 如果过去一定时间
            if cls.active_time > interval:
                cls.active_time = 0

                # 判断是否双倍繁殖
                cur_num = 0
                target_num = 2 if cls.config.double_reproduction and random.random() < cls.config.double_reproduction_rate else 1

                # 尝试一定次数
                for _ in range(100 * target_num):
                    new_plant = cls.create_new_p(cls.config)

                    # 判断该位置能否生成植物
                    if not cls.is_too_close_p(new_plant, plants):

                        # 决定该植物是否有治愈能力
                        if cls.config.is_medicative and random.random() < cls.config.medicative_prob:
                            new_plant.medicative = True
                            if cls.config.image_medicative not in Plant.loaded_images:
                                Plant.loaded_images[cls.config.image_medicative] = pygame.transform.smoothscale(
                                    pygame.image.load(cls.config.image_medicative).convert_alpha(),
                                    (cls.config.size[0] * 2, cls.config.size[1] * 2)
                                )
                            new_plant.image = Plant.loaded_images[cls.config.image_medicative]

                        # 添加植物，增长资源
                        plants.append(new_plant)
                        resource_manager.gain_leafium()

                        # 达到要求则退出
                        cur_num += 1
                        if cur_num >= target_num:
                            break

    @classmethod
    def remove_plants_near_animals(cls, plants: list[Plant], animals: list[Rabbit],
                                   season: Season, resource_manager: ResourceManager, time_speed: int, pause: bool) -> None:
        """移除植物"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - cls.last_remove_time
        cls.last_remove_time = now
        if pause:
            return
        delta_time *= time_speed

        # 判断植物是否有护盾
        if cls.config.is_invincible and cls.invincible_active_time > 0:
            cls.invincible_active_time -= delta_time
            return
        else:
            cls.config.is_invincible = False
            cls.invincible_active_time = 0

        # 找到所有离兔子太近的植物
        plants_to_remove = []
        for plant in plants:
            animal = cls.is_too_close_to_animal(plant, animals)
            if animal:
                plants_to_remove.append(plant)    # 植物加入到待删除列表
                animal.eaten += 1                 # 对应的动物增加吃植物数量
                animal.energy += 1                # 对应的动物增加能量
                if plant.medicative and animal.infected:   # 对应的动物被治愈，并增加一个生态点
                    animal.disinfect()
                    resource_manager.ecopoint += 1
        
        # 统一删除植物
        for plant in plants_to_remove:
            plants.remove(plant)

        # 冬天拥有一定死亡概率
        if season.current == "冬天" and not cls.config.survive_winter:
            for plant in plants[:]:    # 复制列表，避免边遍历边修改
                if random.random() < cls.config.winter_harshness * 0.001:  # 死亡概率：越大越容易死亡
                    plants.remove(plant)

    @staticmethod
    def is_too_close_to_animal(plant: Plant, animals: list[Rabbit]) -> Rabbit | None:
        """判断是否被吃"""
        for animal in animals:
            if getattr(animal, 'herbivore', False):
                distance = ((plant.x - animal.x) ** 2 + (plant.y - animal.y) ** 2) ** 0.5
                if distance < Plant.config.min_animal_distance:
                    return animal
        return None

    @classmethod
    def boost_growth(cls) -> None:
        """触发植物加速生长"""
        cls.config.boosting = True
