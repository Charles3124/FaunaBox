FaunaBox 生态箱模拟系统游戏
一个使用 Python 构建的 2D 生态系统模拟游戏，模拟植物、兔子、鳄鱼三种生命之间的生存、繁殖与捕食关系。

项目结构
FaunaBox/
├── assets/                    # 游戏贴图与音效资源
│   ├── sounds/
│   └── sprites/
├── game/
│   ├── core/                  # 核心程序，包含 World、Clock、ResourceManager 等世界相关的类
│   ├── entities/              # 游戏实体，包含动物、植物、建筑相关的类
│   ├── environment/           # 游戏环境，包含季节、灾害相关的类
│   ├── systems/               # 玩家辅助系统，包含科技树类
│   ├── ui/                    # 游戏的 UI 系统，包含 Button 类
│   ├── utils/                 # 辅助函数与参数配置
│   │   └── config.py          # 所有生物与环境的参数配置
├── tools/
├── main.py                    # 游戏主程序
├── balance.py                 # 数值平衡性模拟器
├── ecosystem_simulation.xlsx  # balance.py 导出的模拟数据
├── README.md                  # 当前文档

游戏机制简述
以下是游戏中的主要生态机制：
生命种类与行为
| 生物   | 行为描述 |
|--------|----------|
| 🌱 植物 | 自动繁殖，被兔子吃 |
| 🐇 兔子 | 寻找植物吃，积累能量后繁殖，被鳄鱼吃 |
| 🐊 鳄鱼 | 寻找兔子吃，积累能量后繁殖，周期性觅食与休息 |

四季系统
游戏内每 15 秒切换一次季节，每一定时间有概率降雨，影响：
- 生物移动速度
- 植物繁殖速度
- 冬季会造成额外的植物死亡

如何运行游戏
1. 安装依赖
使用 Python 3.12，可以使用 Anaconda 创建虚拟环境：

conda create -n faunabox python=3.12
conda activate faunabox
pip install -r requirements.txt

2. 运行游戏

python main.py
参数说明（config.py）
配置集中在 game/utils/config.py 文件内，包含以下部分：

- MapConfig: 地图尺寸
- PlantConfig: 植物大小、繁殖间隔、雨水增益等
- RabbitConfig: 移动速度、觅食范围、繁殖阈值等
- CrocodileConfig: 捕食范围、寿命、繁殖阈值等
- SeasonConfig: 季节切换时间、速度倍率、生长倍率等

TODO / 后续计划
- ⏳ 关卡和游戏流程设计
- ⏳ 更多生物（如老鹰、狼）
- ⏳ 更多灾害事件（如火灾、洪水）
- ⏳ 保存与回放机制

License
本项目仅用于学习、教学与模拟研究，如需商业用途请联系作者。
