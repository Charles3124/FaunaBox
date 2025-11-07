"""
animal_species.py

功能: 定义不同动物种类及行为
时间: 2025/11/07
版本: 1.0
"""

from __future__ import annotations
from typing import Optional
import math
import random
import heapq

import pygame

from .animal import Animal
from .plant import Plant
from game.utils import (MapConfig, RabbitConfig, CrocodileConfig, PlantConfig)
from game.environment import Season


class Crocodile(Animal):
    """Animal 的子类，管理动物鳄鱼的移动、觅食等行为"""

    carnivore = True   # 食肉动物标签

    def __init__(self, x: float, y: float, config: CrocodileConfig):
        super().__init__(x, y, config)
        self.active_time = 0         # 累计活跃时间
        self.boost_active_time = 0   # 累计加速时间
        self.last_update_time = pygame.time.get_ticks()    # 上次检查时间

        self.edge_margin = random.randrange(80, 120)   # 目标边缘间距

        self.hungry = True           # 控制觅食行为
        self.rest_duration = 15000   # 休息时长
        self.eat_num = 0             # 吃兔子的数量
        self.rest_num = 1            # 休息要求吃兔子的数量
        self.full_speed_rate = 0.8   # 吃饱后移速的减少倍率
        self.rest_speed_rate = 0.6   # 游走时移速的减少倍率

    def move(
            self, crocodiles: list[Crocodile], rabbits: list[Rabbit],
            dead_animals: Optional[list[Animal]],
            plants: list[Plant], plant_config: PlantConfig,
            season: Season, time_speed: int, pause: bool
    ) -> None:
        """鳄鱼移动"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now
        if pause:
            return
        delta_time *= time_speed

        # 检测科技树造成的属性变化
        self.update_basic_stats()
        
        # 年龄增长与速度扰动
        self.age += delta_time
        self.speed += random.uniform(-self.speed_change_rate, self.speed_change_rate)
        self.angle += random.uniform(-self.angle_change_rate, self.angle_change_rate)
        self.speed = min(max(self.speed, self.min_speed), self.max_speed)

        # 计算倍速和季节倍率
        self.speed *= time_speed
        self.speed *= season.get_multiplier_a()

        # 是否在加速状态
        if self.config.boosting and self.boost_active_time > 0:
            self.boost_active_time -= delta_time
            self.speed *= self.config.boost_rate
        else:
            self.boost_active_time = 0
            self.config.boosting = False

        # ----- 捕食或休息行为 -----
        # 饥饿时捕食
        if self.hungry:
            prey = self._find_prey(rabbits, self.config.min_hunt_distance)
            if prey:
                self.angle = math.atan2(prey.y - self.y, prey.x - self.x)
                self.angle += random.uniform(-math.pi / 8, math.pi / 8)
                dist = math.hypot(self.x - prey.x, self.y - prey.y)

                # 捕食成功
                if dist < self.config.min_eat_distance:
                    dead_animals.append(prey)
                    self.eaten += 1
                    self.eat_num += 1

                    # 吃饱了就休息
                    if self.eat_num >= self.rest_num:
                        self.eat_num = 0
                        self.hungry = False
        
        # 靠近边缘或徘徊
        else:
            self.active_time += delta_time

            # 判断是否在边缘
            is_near_edge = (
                self.x < self.edge_margin or self.x > MapConfig.width - self.edge_margin or
                self.y < self.edge_margin or self.y > MapConfig.height - self.edge_margin
            )

            # 前往最近边缘
            if not is_near_edge:
                target_x = 0 if self.x < MapConfig.width / 2 else MapConfig.width
                target_y = 0 if self.y < MapConfig.height / 2 else MapConfig.height
                self.angle = math.atan2(target_y - self.y, target_x - self.x)
                self.angle += random.uniform(-math.pi / 6, math.pi / 6)
                self.speed *= self.full_speed_rate
            else:
                # 在边缘，随机游走
                self.speed *= self.rest_speed_rate
            
            # 检查是否超过休息时间
            if self.active_time > self.rest_duration:
                self.active_time = 0
                self.hungry = True  # 进入下一轮捕食

        # ----- 执行移动 -----
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)

        # 边界反弹
        if not (self.size[0] <= self.x + dx <= MapConfig.width - self.size[0]):
            self.angle = math.pi - self.angle
        if not (self.size[1] <= self.y + dy <= MapConfig.height - self.size[1]):
            self.angle = -self.angle

        # 更新位置
        self.x += dx
        self.y += dy
        self.x = max(self.size[0], min(MapConfig.width - self.size[0], self.x))
        self.y = max(self.size[1], min(MapConfig.height - self.size[1], self.y))

    def _find_prey(self, rabbits: list[Rabbit], detection_radius: int) -> Rabbit | None:
        """寻找附近的猎物 herbivore"""
        closest_prey = None
        closest_distance = float('inf')

        for other in rabbits:
            distance = math.hypot(self.x - other.x, self.y - other.y)
            if distance < detection_radius and distance < closest_distance:
                closest_prey = other
                closest_distance = distance
        return closest_prey


class Rabbit(Animal):
    """Animal 的子类，管理动物兔子的移动、觅食等行为"""

    herbivore = True   # 食草动物

    def __init__(self, x: float, y: float, config: RabbitConfig):
        super().__init__(x, y, config)
        self.boost_active_time = 0   # 累计加速时间
        self.last_update_time = pygame.time.get_ticks()   # 上次检查时间

        self.margin = 60             # 边界阈值
        self.escape_weight = 1.0     # 逃离权重
        self.boundary_weight = 1.2   # 边界权重
        self.max_noise = math.pi / 20   # 最大扰动
        self.min_noise = math.pi / 30   # 最小扰动

        self.energy = 0              # 体力值
        self.infected = False        # 是否感染
        self.immune = False          # 是否免疫传染病

    def move(
            self, crocodiles: list[Crocodile], rabbits: list[Rabbit],
            dead_animals: Optional[list[Animal]],
             plants: list[Plant], plant_config: PlantConfig,
            season: Season, time_speed: int, pause: bool
    ) -> None:
        """兔子移动"""
        # 活跃时间检查
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update_time
        self.last_update_time = now
        if pause:
            return
        delta_time *= time_speed

        # 检测科技树造成的属性变化
        self.update_basic_stats()
        
        # 年龄增长
        self.age += delta_time

        # 如果已感染，则加速寿命消耗
        if self.infected:
            self.age += delta_time * self.config.infected_multiplier  # 再额外增长一次，等效于寿命加倍流失

            # 检查传染给其他兔子
            for other in rabbits:
                if other != self and not other.infected:
                    dist = math.hypot(self.x - other.x, self.y - other.y)
                    if dist < self.config.infection_range:
                        other.infect(self.config.image_infected)

        # 速度扰动、吃植物加速、感染减速
        self.speed += random.uniform(-self.speed_change_rate, self.speed_change_rate)

        eat_boost = min(self.energy, self.config.max_eat_boost) * self.config.plant_eat_boost
        infection_down = self.config.infection_speed_down if self.infected else 0

        up_speed = self.max_speed + eat_boost - infection_down
        low_speed = self.min_speed + eat_boost - infection_down

        self.speed = min(max(self.speed, low_speed), up_speed)

        # 角度扰动
        self.angle += random.uniform(-self.angle_change_rate, self.angle_change_rate)

        # 计算倍速和季节倍率
        self.speed *= time_speed
        self.speed *= season.get_multiplier_a()

        # 是否在加速状态
        if self.config.boosting and self.boost_active_time > 0:
            self.boost_active_time -= delta_time
            self.speed *= self.config.boost_rate
        else:
            self.boost_active_time = 0
            self.config.boosting = False

        # ----- 优先级 -----
        # 最优先：找最近捕食者并远离
        pre_center = self._find_predator(crocodiles, self.config.min_croc_distance)
        if pre_center:
            # 逃离方向（远离捕食者 + 预测）
            dx = self.x - pre_center[0]
            dy = self.y - pre_center[1]

            # 边界力（非线性，增强逃离边缘）
            boundary_force_x = self._boundary_force(self.x, self.margin, MapConfig.width - self.margin)
            boundary_force_y = self._boundary_force(self.y, self.margin, MapConfig.height - self.margin)

            # 合成总方向向量（逃离 + 边界）
            combined_dx = dx * self.escape_weight + boundary_force_x * self.boundary_weight
            combined_dy = dy * self.escape_weight + boundary_force_y * self.boundary_weight

            # 检查撞墙并尝试滑动修正
            angle = math.atan2(combined_dy, combined_dx)
            test_dx = self.speed * math.cos(angle)
            test_dy = self.speed * math.sin(angle)

            next_x = self.x + test_dx
            next_y = self.y + test_dy

            # 水平方向撞墙，沿 y 滑动
            if not (self.size[0] <= next_x <= MapConfig.width - self.size[0]):
                angle = math.copysign(math.pi / 2, test_dy)
            
            # 垂直方向撞墙，沿 x 滑动
            if not (self.size[1] <= next_y <= MapConfig.height - self.size[1]):
                angle = 0 if test_dx > 0 else math.pi

            # 增加扰动（根据边界 proximity 调整）
            proximity_x = min(abs(self.x - self.margin), abs(self.x - (MapConfig.width - self.margin))) / self.margin
            proximity_y = min(abs(self.y - self.margin), abs(self.y - (MapConfig.height - self.margin))) / self.margin
            proximity = min(proximity_x, proximity_y)
            noise = max(self.min_noise, self.max_noise * proximity)
            angle += random.uniform(-noise, noise)

            # 应用角度
            self.angle = angle

        else:
            # 最低优先：避免同类过近
            for other in rabbits:
                if other != self:
                    dist = math.hypot(self.x - other.x, self.y - other.y)
                    if dist < self.config.min_distance:
                        avoid_angle = math.atan2(self.y - other.y, self.x - other.x)
                        self.angle = avoid_angle + random.uniform(0, math.pi / 2)
                        break
            
            # 次优先：靠近植物
            if not plant_config.is_invincible:
                all_plants, healing_plants = self._find_plant(plants)

                # 如果自身感染，并且范围里有治愈药草
                if self.infected and healing_plants:
                    target_x, target_y = healing_plants[0][1], healing_plants[0][2]
                    self.angle = math.atan2(target_y - self.y, target_x - self.x)
                    self.angle += random.uniform(-math.pi / 10, math.pi / 10)

                # 如果范围里有普通植物
                elif all_plants:
                    target_x, target_y = all_plants[0][1], all_plants[0][2]
                    self.angle = math.atan2(target_y - self.y, target_x - self.x)
                    self.angle += random.uniform(-math.pi / 10, math.pi / 10)

        # ----- 移动逻辑 -----
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)

        # 边界反弹
        if not (self.size[0] <= self.x + dx <= MapConfig.width - self.size[0]):
            self.angle = math.pi - self.angle
        if not (self.size[1] <= self.y + dy <= MapConfig.height - self.size[1]):
            self.angle = -self.angle

        # 更新位置
        self.x += dx
        self.y += dy
        self.x = max(self.size[0], min(MapConfig.width - self.size[0], self.x))
        self.y = max(self.size[1], min(MapConfig.height - self.size[1], self.y))

    def _find_predator(self, crocodiles: list[Crocodile], detection_radius: int) -> Optional[tuple[float, float]]:
        """寻找最近的食肉动物 carnivore"""
        predators = []
        weights = []
        ε = 1e-3

        for other in crocodiles:
            distance = math.hypot(self.x - other.x, self.y - other.y)
            if distance < detection_radius:
                weight = 1 / (distance ** 2 + ε)  # 越近权重越大
                predators.append((other.x, other.y, weight))
                weights.append(weight)

        if not predators:
            return None

        # 加权平均
        total_weight = sum(weights)
        avg_x = sum(p[0] * p[2] for p in predators) / total_weight
        avg_y = sum(p[1] * p[2] for p in predators) / total_weight
        return avg_x, avg_y

    def _boundary_force(self, pos: float, min_val: int, max_val: int) -> float:
        """计算边界力"""
        if pos < min_val:
            return (min_val - pos) ** 2 / self.margin ** 2
        elif pos > max_val:
            return -(pos - max_val) ** 2 / self.margin ** 2
        return 0.0

    def _find_plant(
            self, plants: list[Plant]
    ) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
        """寻找最近的草和治愈药草"""
        all_plants, healing_plants = [], []

        for plant in plants:
            cur_x, cur_y = plant.x, plant.y
            dist = math.hypot(self.x - cur_x, self.y - cur_y)

            if dist < self.config.min_plant_distance:
                heapq.heappush(all_plants, (dist, cur_x, cur_y))
            
            if plant.medicative and dist < self.config.min_plant_distance_infected:
                heapq.heappush(healing_plants, (dist, cur_x, cur_y))
        
        return all_plants, healing_plants

    def infect(self, virus_image_path: str) -> None:
        """兔子被感染，替换贴图"""
        # 如果免疫，则不感染
        if self.immune:
            return
        
        # 受感染，获得免疫力，下次不会被感染
        self.infected = True
        self.immune = True

        # 替换贴图
        if virus_image_path not in Animal.loaded_images:
            Animal.loaded_images[virus_image_path] = pygame.transform.smoothscale(
                pygame.image.load(virus_image_path).convert_alpha(),
                (self.size[0] * 2, self.size[1] * 2)
            )
        self.image = Animal.loaded_images[virus_image_path]

    def disinfect(self) -> None:
        """兔子被治愈，替换贴图"""
        self.infected = False
        self.image = Animal.loaded_images[self.config.image]
