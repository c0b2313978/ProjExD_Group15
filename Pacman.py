import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 640  # ゲームウィンドウの高さ
PLAYER_SPEED = 3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
GS = 32


class Map:
    def __init__(self):
        """
        マップの初期化
        """
        self.map = [
            [1, 1, 1, 1, 1, 1, 1, 1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1],
            [1, 0, 0, 0, 0, 1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1],
            [1, 0, 1, 1, 0, 1, 0, 1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,1],
            [1, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
            [1, 0, 1, 1, 0, 1, 0, 1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,1],
            [1, 0, 0, 1, 0, 1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,1 ,0 ,0 ,1],
            [1, 1, 0, 0, 0, 1, 1, 1 ,0 ,1 ,0 ,1 ,1 ,1 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,1 ,0 ,0 ,0 ,1 ,1],
            [1, 0, 0, 1, 0, 0, 0, 0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,1],
            [1, 0, 1, 1, 0, 1, 1, 1 ,0 ,1 ,0 ,1 ,1 ,0 ,0 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,1 ,0 ,1],
            [1, 0, 0, 0, 0, 0, 0, 0 ,0 ,1 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
            [1, 1, 0, 1, 1, 1, 0, 1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,1],
            [1, 0, 0, 0, 0, 0, 0, 1 ,0 ,1 ,0 ,1 ,1 ,1 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
            [1, 0, 1, 0, 1, 1, 0, 0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,1 ,1 ,0 ,1 ,0 ,1],
            [1, 0, 0, 0, 1, 1, 0, 1 ,0 ,1 ,1 ,1 ,0 ,1 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,0 ,0 ,1],
            [1, 1, 1, 0, 0, 0, 0, 1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ,1 ,1],
            [1, 0, 0, 0, 1, 1, 0, 1 ,0 ,1 ,0 ,1 ,1 ,1 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,0 ,0 ,1],
            [1, 0, 1, 0, 0, 0, 0, 0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,1],
            [1, 0, 1, 0, 1, 1, 0, 1 ,0 ,1 ,1 ,1 ,0 ,1 ,1 ,0 ,1 ,1 ,1 ,0 ,1 ,0 ,1 ,1 ,0 ,1 ,0 ,1],
            [1, 0, 0, 0, 0, 0, 0, 1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
            [1, 1, 1, 1, 1, 1, 1, 1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1],
        ]
        self.ROW,self.COL = len(self.map),len(self.map[0])

    def draw_map(self, screen):
        """
        マップを描画する
        """
        for r in range(self.ROW):
            for c in range(self.COL):
                if self.map[r][c] == 0: # 道（緑の四角）
                    pg.draw.rect(screen, (0, 255, 0), (c*GS, r*GS, GS, GS))
                elif self.map[r][c] == 1:  # 壁（青の四角）
                    pg.draw.rect(screen, (0, 0, 255), (c*GS, r*GS, GS, GS))

    def is_movable(self, x, y):
        """
        (x,y)は移動可能か？
        """
        # マップ範囲内か？
        if x < 0 or x > self.COL-1 or y < 0 or y > self.ROW-1:
            return False
        # マップチップは移動可能か？
        if self.map[y][x] == 1:  
            return False
        return True


class Player(pg.sprite.Sprite):
    """
    ゲームキャラクター（パックマン）に関するクラス
    """
    def __init__(self, game_map):
        """
        パックマンを生成する
        """
        
        self.x = 50  # 初期X座標
        self.y = 50  # 初期Y座標
        self.radius = 12 # 円の半径
        self.color = (255, 255, 0)  # 円の色（黄色）
        self.map = game_map  # マップインスタンスを参照する

    def draw(self, screen):
        """
        プレイヤー（黄色の円）を描画する
        """
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def can_move(self, next_x, next_y):
        """
        プレイヤーが半径分考慮して、(next_x, next_y)に移動可能かチェックする関数
        複数点チェックでめり込みを防ぐ
        """
        r = self.radius
        # チェックする相対位置(プレイヤー円周を囲むポイント群)
        check_offsets = [
            (-r, 0),
            (r, 0),
            (0, -r),
            (0, r),
            (-r, -r),
            (r, -r),
            (-r, r),
            (r, r)
        ]
        
        for ox, oy in check_offsets:
            tile_x = (next_x + ox) // GS
            tile_y = (next_y + oy) // GS
            if not self.map.is_movable(tile_x, tile_y):
                return False
        return True

    def move(self, keys):
        """
        キー入力に応じてプレイヤーを移動させる
        水平移動と垂直移動を分けて処理する
        """
        next_x, next_y = self.x, self.y

        # 水平移動
        if keys[pg.K_LEFT]:
            new_x = self.x - PLAYER_SPEED
            if self.can_move(new_x, self.y):
                next_x = new_x
        elif keys[pg.K_RIGHT]:
            new_x = self.x + PLAYER_SPEED
            if self.can_move(new_x, self.y):
                next_x = new_x

        # 垂直移動
        if keys[pg.K_UP]:
            new_y = self.y - PLAYER_SPEED
            if self.can_move(next_x, new_y):
                next_y = new_y
        elif keys[pg.K_DOWN]:
            new_y = self.y + PLAYER_SPEED
            if self.can_move(next_x, new_y):
                next_y = new_y

        self.x, self.y = next_x, next_y

    



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

    

class Item(pg.sprite.Sprite):
    """
    アイテムに関するクラス
    """
    def __init__(self, x, y):
        """
        コインを生成する
        """
        super().__init__()
        self.radius = GS // 6 
        self.image = pg.Surface((self.radius * 2, self.radius * 2))
        pg.draw.circle(self.image, (255, 255, 0), (self.radius, self.radius), self.radius)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * GS + GS // 2 - self.radius, y * GS + GS // 2 - self.radius)
        

class Score:
    def __init__(self):
        pass

def draw_start_screen(screen):
    """
    スタート画面を描画する関数
    """
    screen.fill((0,0,0))  # 背景を黒に設定

    #タイトル表示(画面上部に配置)
    font_title=pg.font.Font(None,100)
    title_text=font_title.render("PacmanGame",True,(255,255,0))  #黄色の文字
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))  # 上部（y=50）に配置
     
    # パックマンのイラストを描画
    pacman_center = (WIDTH // 2, HEIGHT // 2 - 50)
    pacman_radius = 100
    pacman_color = (255, 255, 0)  # 黄色
    pacman_mouth_angle = 30  # 口の開き角度

    # パックマンの本体（扇形）を描画
    points = [pacman_center]  # 扇形の頂点リスト
    for angle in range(pacman_mouth_angle, 360 - pacman_mouth_angle + 1, 1):  # 1度ずつ増加
        x = pacman_center[0] + pacman_radius * math.cos(math.radians(angle))
        y = pacman_center[1] - pacman_radius * math.sin(math.radians(angle))
        points.append((x, y))
    pg.draw.polygon(screen, pacman_color, points)  # 塗りつぶした扇形を描画

    # パックマンの目を描画
    eye_position = (pacman_center[0] + pacman_radius // 4, pacman_center[1] - pacman_radius // 2)
    eye_radius = 10
    pg.draw.circle(screen, (0, 0, 0), eye_position, eye_radius)

    # スペースキー案内を表示
    font_subtitle = pg.font.Font(None, 50)  # 中くらいのフォント
    press_space_text = font_subtitle.render("PRESS SPACE KEY", True, (255, 255, 255))  # 白色の文字
    screen.blit(press_space_text, (WIDTH // 2 - press_space_text.get_width() // 2, HEIGHT // 2 + 100))

    # コピーライト表示
    font_copyright = pg.font.Font(None, 30)  # 小さいフォント
    copyright_text = font_copyright.render("(c) 2024 Group15", True, (255, 255, 255))
    screen.blit(copyright_text, (WIDTH - copyright_text.get_width() - 10, HEIGHT - copyright_text.get_height() - 10))


def main():
    pg.display.set_caption("Pacman")
    screen = pg.display.set_mode((WIDTH, HEIGHT))   
    start=True
    d_map = Map()
    # d_map.draw_map(screen)
    player = Player(d_map)

    coins = pg.sprite.Group()
    
    for y in range(len(d_map.map)):
        for x in range(len(d_map.map[0])):
            if d_map.map[y][x] == 0:
                coin = Item(x, y)
                coins.add(coin)

    tmr = 0
    clock = pg.time.Clock()

    while True:
        if start:
            draw_start_screen(screen)  # スタート画面を描画
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:  # スペースキーで開始
                    start = False
                    
        else:
            # ゲーム中の処理を書く
            screen.fill((0, 0, 0))  # 背景を黒に設定
            d_map.draw_map(screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            key_lst = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # キー入力を取得して移動処理
            keys = pg.key.get_pressed()
            player.move(keys)

            # プレイヤー（黄色の円）を描画
            player.draw(screen)

            coins.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()