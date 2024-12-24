import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 640  # ゲームウィンドウの高さ
PLAYER_SPEED = 2
os.chdir(os.path.dirname(os.path.abspath(__file__)))
GS = 32


class Map:
    """マップの管理を行うクラス"""
    def __init__(self, map_file: str) -> None:
        """マップの初期化
        Args:
            map_file: マップデータファイルのパス
        Note:
            ファイルフォーマット:
            0: 通路
            1: 壁
            2: 通常エサ
            3: パワーエサ
            4: 敵のおうち
            5: ワープトンネル
        """
        self.dots_remaining = 0  # 残りドット数
        self.dots_eaten = 0      # 食べたドット数
        
        
        # マップデータの読み込み
        self.map_data = []
        with open(map_file, 'r') as f:
            for line in f:
                row = [int(cell) for cell in line.strip().split()]
                self.map_data.append(row)
        self.height = len(self.map_data)
        self.width = len(self.map_data[0])
        
        # パワーエサとワープトンネルの位置を特定
        power_pellets = []
        for y in range(self.height):
            for x in range(self.width):
                if self.map_data[y][x] == 3:
                    power_pellets.append({'x': x, 'y': y})
        self.power_pellets = power_pellets
        
        tunnels = []
        for y in range(self.height):
            for x in range(self.width):
                if self.map_data[y][x] == 5:
                    tunnels.append({'x': x, 'y': y})
        self.tunnels = tunnels
        
        """プレイフィールドの作成
        playfield: マップの各マスに対応する辞書の2次元配列
        各辞書のキー:
            'path': bool, そのマスが通路であるか
            'dot': int, そのマスにあるドットの種類 (0: なし, 1: 通常ドット, 2: パワードット)
            'intersection': bool, そのマスが交差点であるか
            'tunnel': bool, そのマスがワープトンネルであるか
        """
        playfield = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = {
                    'path': self.map_data[y][x] in [0, 2, 3, 4, 5],
                    'dot': 1 if self.map_data[y][x] == 2 else 2 if self.map_data[y][x] == 3 else 0,
                    'intersection': False,
                    'tunnel': self.map_data[y][x] == 5
                }
                if cell['dot'] > 0:
                    self.dots_remaining += 1
                row.append(cell)
            playfield.append(row)
        
        # 交差点の判定
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if playfield[y][x]['path']:
                    paths = 0
                    if playfield[y-1][x]['path']: paths += 1
                    if playfield[y+1][x]['path']: paths += 1
                    if playfield[y][x-1]['path']: paths += 1
                    if playfield[y][x+1]['path']: paths += 1
                    playfield[y][x]['intersection'] = paths > 2
        self.playfield = playfield

        # 敵の初期位置を特定
        self.enemy_start_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.map_data[y][x] == 4:
                    self.enemy_start_positions.append((x, y))
    
    def draw(self, screen: pg.Surface, field_start: tuple[int, int]) -> None:
        """マップを描画する
        Args:
            screen: 描画対象の画面
            field_start: フィールドの開始座標(x, y)
        """
        colors = {
            0: (0, 0, 0),      # 通路: 黒
            1: (54, 67, 100),  # 壁: 青
            4: (255, 192, 203) # ゴーストの家の入り口: ピンク
        }
        
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                rect_x = field_start[0] + (x * GRID_SIZE)
                rect_y = field_start[1] + (y * GRID_SIZE)
                
                if cell in colors:
                    pg.draw.rect(screen, colors[cell], (rect_x, rect_y, GRID_SIZE, GRID_SIZE))


class Player(pg.sprite.Sprite):
    """
    ゲームキャラクター（パックマン）に関するクラス
    """
    def __init__(self, game_map):
        """
        パックマンを生成する
        """
        super().__init__()
        self.x = 50  # 初期X座標
        self.y = 50  # 初期Y座標
        self.radius = 12 # 円の半径
        self.color = (255, 255, 0)  # 円の色（黄色）
        self.map = game_map  # マップインスタンスを参照する
        self.image = pg.Surface((self.radius * 2, self.radius * 2))
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(self.x, self.y)) 
        self.last_direction = None  #最後に押された方向を保持
        self.next_direction = None

    def draw(self, screen):
        """
        プレイヤー（黄色の円）を描画する
        """
        screen.blit(self.image, self.rect)

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
    
    def is_at_corner(self):
        """
        プレイヤーが角にいるかどうかを判定
        """
        r = self.radius
        check_offsets = [
            (-r, 0),
            (r, 0),
            (0, -r),
            (0, r),
        ]
        
        #移動できる方向をカウント
        possible_directions = 0
        for dx,dy in check_offsets:
          next_rect=self.rect.move(dx,dy)
          if self.map.is_movable(next_rect):
              possible_directions += 1

        # 2方向以上移動可能なら角とみなす
        return possible_directions >= 3

    def move(self, keys):
        """
        キー入力に応じてプレイヤーを移動させる
        """
        dx, dy = 0, 0  # 移動量

        # 現在の方向のまま進むための移動量
        if self.last_direction == "left":
            dx, dy = -PLAYER_SPEED, 0
        elif self.last_direction == "right":
            dx, dy = PLAYER_SPEED, 0
        elif self.last_direction == "up":
            dx, dy = 0, -PLAYER_SPEED
        elif self.last_direction == "down":
            dx, dy = 0, PLAYER_SPEED

        # 次の方向の移動をチェック
        if self.next_direction:
            temp_dx, temp_dy = 0, 0
            if self.next_direction == "left":
                temp_dx, temp_dy = -PLAYER_SPEED, 0
            elif self.next_direction == "right":
                temp_dx, temp_dy = PLAYER_SPEED, 0
            elif self.next_direction == "up":
                temp_dx, temp_dy = 0, -PLAYER_SPEED
            elif self.next_direction == "down":
                temp_dx, temp_dy = 0, PLAYER_SPEED

            # 次の方向が移動可能なら方向転換
            if self.map.is_movable(self.rect.move(temp_dx, temp_dy)):
                self.last_direction = self.next_direction
                dx, dy = temp_dx, temp_dy
                self.next_direction = None

        # 現在の方向で移動可能か判定
        next_rect = self.rect.move(dx, dy)
        if self.map.is_movable(next_rect):
            self.rect = next_rect
            self.x, self.y = self.rect.center
        else:
            # 現在の方向で動けない場合は停止
            dx, dy = 0, 0

        # キー入力を次の方向として記録
        if keys[pg.K_LEFT]:
            self.next_direction = "left"
        elif keys[pg.K_RIGHT]:
            self.next_direction = "right"
        elif keys[pg.K_UP]:
            self.next_direction = "up"
        elif keys[pg.K_DOWN]:
            self.next_direction = "down"


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
    def __init__(self, x: int , y:int):
        """
        コインを生成する
        x, y : mapの通路の部分
        """
        super().__init__()
        self.radius = GS // 6 
        self.image = pg.Surface((self.radius * 2, self.radius * 2))
        pg.draw.circle(self.image, (255, 255, 0), (self.radius, self.radius), self.radius)  # 半径radiusの円を描く
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * GS + GS // 2 - self.radius, y * GS + GS // 2 - self.radius)  # rectの左上の座標
        

class Score:
    """
    コインを獲得したときスコアとして表示するクラス
    コイン1枚：50点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 40)  # サイズは40
        self.color = (255, 255, 255)  # カラーは白
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH - 110, HEIGHT - 150

    def update(self, screen: pg.Surface):  
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)  


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
    score = Score()
    
    #コインの生成
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

            # playerとコインの値判定
            hit_coins = pg.sprite.spritecollide(player, coins, False)
            for coin in hit_coins:
                coins.remove(coin)
                score.value += 50
            coins.draw(screen)

            score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()