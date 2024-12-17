import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Map:
    def __init__(self):
        pass 


class Player:
    def __init__(self):
        pass


class Enemy:
    def __init__(self):
        pass

class Item:
    """
    アイテムに関するクラス
    """
    def __init__(self):
        """
        アイテムを生成する
        """
        self.image = pg.Surface((10, 10))
        pg.draw.circle(self.image, (255, 255, 0), (10, 10), 10)
        self.rect = self.image.get_rect


class Score:
    def __init__(self):
        pass

    

def main():
    pg.display.set_caption("Pacman")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            pass

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
