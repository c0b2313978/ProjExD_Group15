import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
PLAYER_SPEED = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Map:
    def __init__(self):
        pass 


class Player(pg.sprite.Sprite):
    """
    ゲームキャラクター（パックマン）に関するクラス
    """
    def __init__(self):
        """
        パックマンを生成する
        """
        self.x = 50  # 初期X座標
        self.y = 50  # 初期Y座標
        self.radius = 25  # 円の半径
        self.color = (255, 255, 0)  # 円の色（黄色）
        # self.map = map_data  # マップデータ

    def draw(self, screen):
        """
        プレイヤー（黄色の円）を描画する
        """
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)
       
        

    def move(self, keys):
        """
          移動処理（壁を通り抜けない）
        """
        if keys[pg.K_LEFT]:
            self.x -= PLAYER_SPEED  # 左へ移動
        if keys[pg.K_RIGHT]:
            self.x += PLAYER_SPEED  # 右へ移動
        if keys[pg.K_UP]:
            self.y -= PLAYER_SPEED  # 上へ移動
        if keys[pg.K_DOWN]:
            self.y += PLAYER_SPEED  # 下へ移動
        
    #     for key, d in Player.delta.items():
    #         if keys[key]:
    #             # 次の座標を計算
    #             next_x = self.rect.x + d[0] * self.speed
    #             next_y = self.rect.y + d[1] * self.speed
    #             # マス目に変換（マップデータに対応する位置）
    #             grid_x = next_x // 50
    #             grid_y = next_y // 50

    #             # マップの範囲内かつ壁でない場合のみ移動
    #             if (0 <= grid_x < len(self.map[0]) and 
    #                 0 <= grid_y < len(self.map) and 
    #                 self.map[grid_y][grid_x] == 0):
    #                 self.rect.x = next_x
    #                 self.rect.y = next_y


class Enemy:
    def __init__(self):
        pass

class Item:
    def __init__(self):
        pass


class Score:
    def __init__(self):
        pass




def main():
    pg.display.set_caption("Pacman")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    player = Player()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        screen.fill((0, 0, 0))
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        keys = pg.key.get_pressed()
        player.move(keys)
           
        player.draw(screen)

        

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
