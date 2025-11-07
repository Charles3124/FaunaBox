# config.py
"""游戏实体和系统属性配置"""

import math
from dataclasses import dataclass, field
from pathlib import Path


# 游戏资源路径
BASE_PATH = Path("D:/My Programs/FaunaBox")   # 根目录
SOUNDS_PATH = BASE_PATH / 'assets/sounds'     # 声音资源

SPRITES_PATH = BASE_PATH / 'assets/sprites'   # 图片资源根目录
ANIMAL_PATH = SPRITES_PATH / 'animals'        # 动物图片资源
PLANT_PATH = SPRITES_PATH / 'plants'          # 植物图片资源
BUILDING_PATH = SPRITES_PATH / "buildings"    # 建筑图片资源
ITEM_PATH = SPRITES_PATH / "items"            # 道具图片资源


@dataclass
class MapConfig:
    """地图属性配置"""

    width: int = 1280   # 地图宽度
    height: int = 800   # 地图高度


@dataclass
class RabbitConfig:
    """兔子属性配置"""
    
    # 贴图
    image: str = ANIMAL_PATH / 'rabbit.png'   # 兔子贴图
    image_infected: str = ANIMAL_PATH / 'rabbit_infected.png'   # 感染兔子贴图

    # 基础属性
    initial_num: int = 8              # 初始数量
    size: tuple = (30 // 2, 40 // 2)  # 兔子大小

    min_distance: int = 50            # 兔子间最小距离
    min_plant_distance: int = 60      # 觅食范围
    min_plant_distance_infected: int = 150   # 寻找治愈性药草的范围
    min_croc_distance: int = 200      # 躲避鳄鱼的范围

    ave_speed: float = 0.9            # 速度平均值
    range_speed: float = 0.2          # 速度范围
    speed_change_rate: float = 0.05           # 速度随机变化范围
    angle_change_rate: float = math.pi / 12   # 角度随机变化范围
    plant_eat_boost: float = 0.15     # 吃植物加速幅度
    max_eat_boost: int = 2            # 吃植物的最大加速次数

    reproduction_threshold: dict = field(default_factory=lambda: {'春天': 3, '夏天': 3, '秋天': 3, '冬天': 4})  # 四季兔子的繁殖阈值
    reproduction_resource: int = 3    # 繁殖时增加的资源

    ave_age: int = 3                  # 年龄平均值
    range_age: int = 0.5              # 年龄范围

    # 特殊属性
    boosting: bool = False            # 加速状态
    boost_rate: float = 1.5           # 加速比例
    boost_duration: int = 10000       # 加速时长

    infection_range: int = 80           # 传染半径
    infected_multiplier: int = 2        # 感染后寿命流失倍速
    infection_speed_down: float = 0.3   # 感染后速度降低


@dataclass
class CrocodileConfig:
    """鳄鱼属性配置"""

    # 贴图
    image: str = ANIMAL_PATH / 'crocodile.png'   # 鳄鱼贴图

    # 基础属性
    initial_num: int = 2              # 初始数量
    size: tuple = (40 // 2, 40 // 2)  # 鳄鱼大小

    min_distance: int = 100           # 鳄鱼间最小距离
    min_hunt_distance: int = 500      # 觅食范围
    min_eat_distance: int = 40        # 进食范围

    ave_speed: float = 1.2            # 速度平均值
    range_speed: float = 0.2          # 速度范围
    speed_change_rate: float = 0.05           # 速度随机变化范围
    angle_change_rate: float = math.pi / 12   # 角度随机变化范围

    reproduction_threshold: dict = field(default_factory=lambda: {'春天': 6, '夏天': 6, '秋天': 6, '冬天': 6})  # 四季鳄鱼的繁殖阈值
    reproduction_resource: int = 5    # 繁殖时增加的资源

    ave_age: int = 4                  # 年龄平均值
    range_age: int = 0.5              # 年龄范围

    # 特殊属性
    boosting: bool = False            # 加速状态
    boost_rate: float = 2             # 加速比例
    boost_duration: int = 10000       # 加速时长


@dataclass
class PlantConfig:
    """植物属性配置"""

    # 贴图
    image: str = PLANT_PATH / 'grass.png'     # 植物贴图
    image_medicative: str = PLANT_PATH / 'grass_medicative.png'   # 治愈性植物贴图

    # 基础属性
    initial_num: int = 20              # 初始数量
    size: tuple = (20 // 2, 20 // 2)   # 植物大小

    min_distance: int = 50             # 植物间最小距离
    min_animal_distance: int = 20      # 被吃范围

    reproduction_interval: int = 2000  # 繁殖时间间隔

    # 特殊属性
    boosting: bool = False         # 加速状态
    boost_rate: float = 0.5        # 加速比例
    boost_duration: int = 10000    # 加速时长
    
    rain_bonus: float = 0.8        # 雨水增益倍率
    winter_harshness: float = 1.0  # 冬天植物死亡倍率
    is_fragile: bool = False       # 冬天是否脆弱
    survive_winter: bool = False   # 是否免疫寒冷

    double_reproduction: bool = False      # 双倍繁殖
    double_reproduction_rate: float = 0.2  # 双倍繁殖概率

    is_medicative: bool = False        # 是否有治愈性
    medicative_prob: float = 0.5       # 治愈概率
    medicative_duration: int = 30000   # 持续时间

    is_invincible: bool = False        # 是否有护盾
    invincible_duration: int = 10000   # 护盾时间


@dataclass
class SeasonConfig:
    """季节属性配置"""

    switch_interval: int = 15000    # 季节切换间隔
    speed_multipliers: dict = field(default_factory=lambda: {'春天': 1.0, '夏天': 1.1, '秋天': 1.0, '冬天': 0.6})  # 四季动物移速倍率
    interval_multipliers: dict = field(default_factory=lambda: {'春天': 0.75, '夏天': 1.0, '秋天': 1.25, '冬天': 2.0})  # 四季植物生长倍率
    rain_probability: float = 0.25  # 降雨概率
