"""
animal.py

功能: 创建和管理动物实体
时间: 2025/11/07
版本: 1.0
"""

from __future__ import annotations
from typing import Optional
import random
import math

import pygame

from game.utils import (MapConfig, RabbitConfig, CrocodileConfig)
from game.core import ResourceManager
from game.environment import Season


AnimalConfig = RabbitConfig | CrocodileConfig


class Animal:
    """管理动物的创建、繁殖、死亡等事件"""

    loaded_images = {}

    def __init__(self, x: float, y: float, config: AnimalConfig):
        # 基本属性
        self.config = config
        self.x = x
        self.y = y
        self.size = config.size

        if config.image not in Animal.loaded_images:
            Animal.loaded_images[config.image] = pygame.transform.smoothscale(
                pygame.image.load(config.image).convert_alpha(),
                (self.size[0] * 2, self.size[1] * 2)
            )
        self.image = Animal.loaded_images[config.image]

        # 速度属性
        self.ave_speed = config.ave_speed
        self.range_speed = config.range_speed
        self.min_speed = self.ave_speed - self.range_speed
        self.max_speed = self.ave_speed + self.range_speed
        self.speed = random.uniform(self.min_speed, self.max_speed)
        self.speed_change_rate = config.speed_change_rate

        # 角度属性
        self.angle = random.uniform(0, 2 * math.pi)
        self.angle_change_rate = config.angle_change_rate

        # 年龄属性
        self.age = 0
        self.ave_age = config.ave_age
        self.range_age = config.range_age
        self.age_random = 60000 * random.uniform(self.ave_age - self.range_age, self.ave_age + self.range_age)

        # 实时变化的属性
        self.eaten = 0.0

    def draw(self, screen: pygame.surface.Surface) -> None:
        """绘制动物"""
        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)

    @staticmethod
    def remove_old_animals(animals: list[Animal]) -> Optional[list[Animal]]:
        """移除动物"""
        return [animal for animal in animals if animal.age < animal.age_random]

    @classmethod
    def _is_too_close_a(cls, new_animal: Animal, animals: list[Animal], config: AnimalConfig) -> bool:
        """控制动物距离"""
        for animal in animals:
            distance = (new_animal.x - animal.x) ** 2 + (new_animal.y - animal.y) ** 2
            if distance < config.min_distance_square:
                return True
        return False

    @staticmethod
    def _calculate_new_pos(config: AnimalConfig) -> tuple[float, float]:
        new_x = random.uniform(config.size[0], MapConfig.width - config.size[0])
        new_y = random.uniform(config.size[1], MapConfig.height - config.size[1])
        return new_x, new_y

    @classmethod
    def initialize_animals(cls, config: AnimalConfig) -> list[Animal]:
        """初始化动物"""
        animals = []
        for _ in range(config.initial_num):
            for _ in range(100):
                new_x, new_y = cls._calculate_new_pos(config)
                new_animal = cls(new_x, new_y, config)
                if not cls._is_too_close_a(new_animal, animals, config):
                    animals.append(new_animal)
                    break
        return animals

    @classmethod
    def add_new_animal(
            cls, animals: list[Animal], config: AnimalConfig, all_animals: list[Animal],
            resource_manager: ResourceManager, season: Season
    ) -> list[Animal]:
        """动物繁殖"""
        new_animals = []
        target_eaten = config.reproduction_threshold[season.current]

        for animal in animals:
            if animal.eaten >= target_eaten:
                animal.eaten -= target_eaten

                if getattr(animal, "herbivore", False):
                    animal.energy = 0
                
                for _ in range(100):
                    new_x, new_y = cls._calculate_new_pos(config)
                    new_animal = cls(new_x, new_y, config)
                    if not cls._is_too_close_a(new_animal, all_animals, config):
                        new_animals.append(new_animal)
                        resource_manager.gain_animite(config.reproduction_resource)
                        break

        return new_animals

    @classmethod
    def boost_speed(cls, config: AnimalConfig) -> None:
        """触发动物加速"""
        config.boosting = True

    def update_basic_stats(self) -> None:
        """更新基础属性"""
        # 动物速度有变化
        if self.ave_speed != self.config.ave_speed:
            self.ave_speed = self.config.ave_speed
            self.min_speed = self.ave_speed - self.range_speed
            self.max_speed = self.ave_speed + self.range_speed
            self.speed = random.uniform(self.min_speed, self.max_speed)

        # 动物年龄有变化
        if self.ave_age != self.config.ave_age or self.range_age != self.config.range_age:
            self.ave_age = self.config.ave_age
            self.range_age = self.config.range_age
