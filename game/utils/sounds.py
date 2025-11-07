"""
sounds.py

功能: 游戏声音系统
时间: 2025/11/07
版本: 1.0
"""

import os
import random

import pygame

from game.utils import SOUNDS_PATH


class SoundManager:
    """管理声音播放、停止等事件"""

    def __init__(self, sound_folder: str = SOUNDS_PATH):
        pygame.mixer.init()
        self.sound_dict = self.load_all_sounds(sound_folder)
        self.bgms = ()
        self.bgms_num = len(self.bgms)
        self.set_volume()

    @staticmethod
    def load_all_sounds(sound_folder: str) -> dict[str, pygame.mixer.Sound]:
        """递归加载所有 .ogg、.wav、.mp3 音效文件"""
        sounds = {}
        for root, _, files in os.walk(sound_folder):
            for filename in files:
                if filename.lower().endswith((".ogg", ".wav", ".mp3")):
                    name = os.path.splitext(filename)[0]
                    full_path = os.path.join(root, filename)
                    try:
                        sounds[name] = pygame.mixer.Sound(full_path)
                    except Exception as e:
                        print(f"加载音效失败: {filename} - {e}")
        return sounds

    def set_volume(self) -> None:
        """调整音量大小"""
        self.sound_dict["click_settings1"].set_volume(0.8)
        self.sound_dict["click_tech"].set_volume(0.2)
        self.sound_dict["rain"].set_volume(0.5)

    def play_random_bgm(self) -> None:
        """播放随机音乐"""
        if self.bgms_num > 0:
            random_num = random.randrange(self.bgms_num)
            self.sound_dict[self.bgms[random_num]].play(-1)

    def stop_all_bgm(self) -> None:
        """停止所有音乐"""
        self.sound_dict["rain"].stop()
        if self.bgms_num > 0:
            for bgm in self.bgms:
                self.sound_dict[bgm].stop()


# 创建全局声音管理器实例
sound_manager = SoundManager()
