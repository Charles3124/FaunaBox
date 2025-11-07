"""
plant.py

功能: 创建和管理植物实体
时间: 2025/11/07
版本: 1.0
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import random

import pygame

from game.utils import (MapConfig, PlantConfig)
from game.core import ResourceManager
from game.environment import Season


if TYPE_CHECKING:
    from game.entities import Rabbit


class Plant:
    """管理植物的创建、繁殖、死亡等事件"""

    config: PlantConfig = None
    active_time = 0
    states = {
        "boosting": 0,
        "is_medicative": 0,
        "is_invincible": 0,
    }
    last_update_time = pygame.time.get_ticks()
    last_remove_time = pygame.time.get_ticks()
    loaded_images = {}
    
    def __init__(self, x: float, y: float, config: PlantConfig):
        self.x = x
        self.y = y
        self.size = config.size

        self._load_image(config.image)
        self._load_image(config.image_medicative)
        self.image = Plant.loaded_images[config.image]

        self.medicative = False   # 是否有治愈性

    @classmethod
    def _load_image(cls, image_path: str) -> None:
        """预加载贴图资源"""
        if image_path not in cls.loaded_images:
            cls.loaded_images[image_path] = pygame.transform.smoothscale(
                pygame.image.load(image_path).convert_alpha(),
                (cls.config.size[0] * 2, cls.config.size[1] * 2)
            )

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制植物"""
        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)

    @staticmethod
    def _is_too_close_p(new_plant: Plant, plants: list[Plant]) -> bool:
        """控制植物距离"""
        for plant in plants:
            distance = (new_plant.x - plant.x) ** 2 + (new_plant.y - plant.y) ** 2
            if distance < Plant.config.min_distance ** 2:
                return True
        return False

    @staticmethod
    def _create_new_plant(config: PlantConfig) -> Plant:
        """新建一个植物实例"""
        new_x = random.uniform(config.size[0], MapConfig.width - config.size[0])
        new_y = random.uniform(config.size[1], MapConfig.height - config.size[1])
        return Plant(new_x, new_y, config)

    @classmethod
    def initialize_plants(cls, num_plants: int) -> list[Plant]:
        """初始化植物"""
        plants = []
        for _ in range(num_plants):
            for _ in range(100):
                new_plant = cls._create_new_plant(cls.config)
                if not cls._is_too_close_p(new_plant, plants):
                    plants.append(new_plant)
                    break
        return plants

    @classmethod
    def add_new_plant(
            cls, plants: list[Plant],
            season: Season, resource_manager: ResourceManager,
            time_speed: int, pause: bool
    ) -> None:
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
            if cls._update_state("boosting", delta_time):
                interval = base_interval * cls.config.boost_rate   # 加速生长
            else:
                interval = base_interval

            # 判断是否拥有治愈能力
            cls._update_state("is_medicative", delta_time)

            # 如果过去一定时间
            if cls.active_time > interval:
                cls.active_time = 0

                # 判断是否双倍繁殖
                cur_num = 0
                if cls.config.double_reproduction and random.random() < cls.config.double_reproduction_rate:
                    target_num = 2
                else:
                    target_num = 1

                # 尝试一定次数
                for _ in range(100 * target_num):
                    new_plant = cls._create_new_plant(cls.config)

                    # 判断该位置能否生成植物
                    if not cls._is_too_close_p(new_plant, plants):

                        # 决定该植物是否有治愈能力
                        if cls.config.is_medicative and random.random() < cls.config.medicative_prob:
                            new_plant.medicative = True
                            new_plant.image = Plant.loaded_images[cls.config.image_medicative]

                        # 添加植物，增长资源
                        plants.append(new_plant)
                        resource_manager.gain_leafium()

                        # 达到要求则退出
                        cur_num += 1
                        if cur_num >= target_num:
                            break

    @classmethod
    def remove_plants_near_animals(
            cls, plants: list[Plant], animals: list[Rabbit],
            season: Season, resource_manager: ResourceManager,
            time_speed: int, pause: bool
    ) -> None:
        """移除植物"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - cls.last_remove_time
        cls.last_remove_time = now
        if pause:
            return
        delta_time *= time_speed

        # 判断植物是否有护盾
        if cls._update_state("is_invincible", delta_time):
            return

        # 找到所有离兔子太近的植物
        plants_to_remove = []
        for plant in plants:
            animal = cls._is_too_close_a(plant, animals)
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
            withering_prob = 0.1 / 100 * cls.config.winter_harshness
            if cls.config.is_fragile:
                withering_prob *= 2

            for plant in plants[:]:    # 复制列表，避免边遍历边修改
                if random.random() < withering_prob:  # 死亡概率，越大越容易死亡
                    plants.remove(plant)
        
        elif season.current == "春天":
            cls.config.is_fragile = False

    @staticmethod
    def _is_too_close_a(plant: Plant, animals: list[Rabbit]) -> Rabbit | None:
        """判断是否被吃"""
        for animal in animals:
            if getattr(animal, "herbivore", False):
                distance = (plant.x - animal.x) ** 2 + (plant.y - animal.y) ** 2
                if distance < Plant.config.min_animal_distance ** 2:
                    return animal
        return None

    @classmethod
    def boost_growth(cls) -> None:
        """触发植物加速生长"""
        cls.config.boosting = True

    @classmethod
    def _update_state(cls, state: str, delta_time: int) -> bool:
        """更新状态"""
        if getattr(cls.config, state, False) and cls.states[state] > 0:
            cls.states[state] -= delta_time
            return True
        else:
            cls.states[state] = 0
            setattr(cls.config, state, False)
            return False
