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


class Enemy(pg.sprite.Sprite):

    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]

    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.transform.rotozoom(random.choice(__class__.imgs), 0, 0.8)
        self.rect = self.image.get_rect()
        self.rect.center = xy

        self.vx, self.vy = 0, 0  # 単位時間当たりの移動量
        self.state = "normal"  # "normal" or "weakening"
        self.action = "active"  # active or passive
        self.map = None # Mapクラスのインスタンスを保持するための変数
        self.player = None # Playerクラスのインスタンスを保持するための変数

    def update(self):
        if self.action == "active":
            if self.player: # playerが設定されているか確認
                self.move_towards_player()
        else:
            self.vx, self.vy = 0, 0
        
        self.rect.move_ip(self.vx, self.vy)

    def set_map(self, map):
        """マップ情報を設定する"""
        self.map = map

    def set_player(self, player):
        """プレイヤー情報を設定する"""
        self.player = player

    def move_towards_player(self):
        """プレイヤーの位置に向かって移動する"""
        if not self.map or not self.player:
            return # mapまたはplayerが設定されていない場合は移動しない

        start = (self.rect.centerx // 50, self.rect.centery // 50) # マップのマス目単位での座標に変換
        goal = (self.player.rect.centerx // 50, self.player.rect.centery // 50) # マップのマス目単位での座標に変換

        path = self.bfs(start, goal)
        if path and len(path) > 1:
            next_pos = path[1] # 次の移動先を取得
            self.vx = next_pos[0] - start[0]
            self.vy = next_pos[1] - start[1]
            # マス目単位の移動量をピクセル単位に変換
            self.vx *= 5
            self.vy *= 5
        else:
            self.vx, self.vy = 0, 0 # 移動経路がない場合は停止

    def bfs(self, start, goal):
        """幅優先探索で最短経路を求める"""
        queue = [(start, [start])] # キューに(現在位置, 経路)のタプルを追加
        visited = {start} # 訪問済みのマスを記録するセット

        while queue:
            (current, path) = queue.pop(0)
            if current == goal:
                return path # ゴールに到達したら経路を返す

            x, y = current
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # 上下左右のマスを探索
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map) and self.map[ny][nx] == 0 and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [(nx, ny)])) # キューに次のマスと経路を追加
                    visited.add((nx, ny)) # 訪問済みにする
        return None # 経路が見つからなかった場合はNoneを返す

    def status_update(self):
        pass

    def check_collision(self):
        """プレイヤーとの衝突判定"""
        if self.state == "weakening" and self.rect.colliderect(self.player.rect):
            self.kill() # 敵を消滅させる
            return True
        return False

    

class Item:
    def __init__(self):
        pass


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
