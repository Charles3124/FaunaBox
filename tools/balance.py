import math
from dataclasses import dataclass
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd

from game.utils.config import (MapConfig, RabbitConfig, CrocodileConfig, PlantConfig, SeasonConfig)


# 配置加载
map_cfg = MapConfig()
rabbit_cfg = RabbitConfig()
croc_cfg = CrocodileConfig()
plant_cfg = PlantConfig()
season_cfg = SeasonConfig()

# 常量定义
MAP_AREA = map_cfg.width * map_cfg.height
SEASON_LIST = ('春天', '夏天', '秋天', '冬天')
SEASON_DURATION = season_cfg.switch_interval / 1000
SEASON_NUM = 100

# 初始数量（整数）
plant_count = plant_cfg.initial_num
rabbit_count = rabbit_cfg.initial_num
croc_count = croc_cfg.initial_num

# 累积池定义
@dataclass
class Accumulator:
    value: float = 0.0

    def add(self, amount: float) -> int:
        self.value += amount
        take = int(self.value)
        self.value -= take
        return take

plant_growth_acc = Accumulator()
plant_eaten_acc = Accumulator()
rabbit_birth_acc = Accumulator()
rabbit_eaten_acc = Accumulator()
rabbit_death_acc = Accumulator()
croc_birth_acc = Accumulator()
croc_death_acc = Accumulator()

def estimate_plant_eaten(plant_count, rabbit_count, min_plant_distance, speed):
    """兔子吃植物数量估算"""
    effective_area = math.pi * min_plant_distance ** 2 + 2 * min_plant_distance * speed * SEASON_DURATION
    plant_density = plant_count / MAP_AREA
    plants_per_rabbit = effective_area * plant_density
    return rabbit_count * plants_per_rabbit * 3  # 经验系数

# 数据记录
data = []

for i in range(SEASON_NUM):
    season = SEASON_LIST[i % 4]

    # --- 植物 ---
    interval_multiplier = season_cfg.interval_multipliers[season]
    plant_interval = plant_cfg.reproduction_interval * interval_multiplier / 1000
    growth_float = SEASON_DURATION / plant_interval
    plant_growth = plant_growth_acc.add(growth_float)

    rabbit_speed = rabbit_cfg.ave_speed * season_cfg.speed_multipliers[season]
    eaten_float = estimate_plant_eaten(plant_count, rabbit_count, rabbit_cfg.min_plant_distance, rabbit_speed)
    plant_eaten = plant_eaten_acc.add(min(eaten_float, plant_count))

    plant_count = max(plant_count + plant_growth - plant_eaten, 0)

    # --- 兔子 ---
    rabbit_threshold = rabbit_cfg.reproduction_threshold[season]
    rabbit_birth = rabbit_birth_acc.add(plant_eaten / rabbit_threshold)
    rabbit_eaten = rabbit_eaten_acc.add(croc_count * SEASON_DURATION / 20)
    rabbit_death = rabbit_death_acc.add(SEASON_DURATION / (rabbit_cfg.ave_age * 60) * rabbit_count)

    rabbit_count = max(rabbit_count + rabbit_birth - rabbit_eaten - rabbit_death, 0)

    # --- 鳄鱼 ---
    croc_threshold = croc_cfg.reproduction_threshold[season]
    croc_birth = croc_birth_acc.add(rabbit_eaten / croc_threshold)
    croc_death = croc_death_acc.add(SEASON_DURATION / (croc_cfg.ave_age * 60) * croc_count)

    croc_count = max(croc_count + croc_birth - croc_death, 0)

    # --- 数据记录 ---
    data.append({
        "季节": season,
        "植物繁殖": plant_growth,
        "植物减少": plant_eaten,
        "植物数量": plant_count,

        "兔子繁殖": rabbit_birth,
        "兔子被吃": rabbit_eaten,
        "兔子死亡": rabbit_death,
        "兔子数量": rabbit_count,

        "鳄鱼繁殖": croc_birth,
        "鳄鱼死亡": croc_death,
        "鳄鱼数量": croc_count
    })

    if any(x == 0 for x in (plant_count, rabbit_count, croc_count)):
        data.append({
            "季节": "终止",
            "植物数量": plant_count,
            "兔子数量": rabbit_count,
            "鳄鱼数量": croc_count
        })
        break

# 保存
df = pd.DataFrame(data)
df.to_excel("tools/ecosystem_simulation.xlsx", index=False)
print(df)
