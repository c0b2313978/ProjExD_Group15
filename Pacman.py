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

    def is_movable(self, rect):
        """
        rect が移動可能か？
        """
        # rect の各辺の座標をタイル座標に変換
        left_tile = rect.left // GS
        right_tile = rect.right // GS
        top_tile = rect.top // GS
        bottom_tile = rect.bottom // GS

        # マップ範囲外に出ていないかチェック
        if left_tile < 0 or right_tile >= self.COL or top_tile < 0 or bottom_tile >= self.ROW:
          return False

        # 各タイルが移動可能かチェック
        for x in range(left_tile, right_tile + 1):
           for y in range(top_tile, bottom_tile + 1):
            if self.map[y][x] == 1: #壁があったら
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


class EnemyMode(Enum):
    """敵の行動モードを定義する列挙型"""
    CHASE = auto()      # 追跡モード
    TERRITORY = auto()  # 縄張りモード
    WEAK = auto()       # 弱体化モード


class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_id: int, player: 'Player', map_data: 'Map') -> None:
        """敵キャラクターの初期化
        Args:
            enemy_id: 敵の識別番号（1-4）
            player: プレイヤーオブジェクト
            map_data: マップデータ
        """
        super().__init__()
        self.enemy_id = enemy_id
        self.player = player
        self.map_data = map_data
        
        # 画像の読み込みとスケーリング
        self.normal_image = pg.transform.scale(
            pg.image.load(f"fig/{enemy_id}.png").convert_alpha(), 
            (ENEMY_SIZE, ENEMY_SIZE)
        )
        self.weak_image = pg.transform.scale(
            pg.image.load("fig/chicken.png").convert_alpha(), 
            (ENEMY_SIZE, ENEMY_SIZE)
        )
        self.eaten_image = pg.transform.scale(
            pg.image.load("fig/pet_hone.png").convert_alpha(), 
            (ENEMY_SIZE, ENEMY_SIZE)
        )
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        
        # 初期位置の設定
        self.start_pos = map_data.enemy_start_positions[enemy_id-1]
        self.rect.center = get_pixel_pos(*self.start_pos)
        
        # 移動関連の初期化
        self.default_speed = 2
        self.speed = self.default_speed
        self.current_path = []
        self.moving = False
        
        # スタート時の遅延設定
        self.start_delay = enemy_id * 1  # 敵ごとのスタート遅延
        self.game_start_time = time.time()
        self.can_move = False
        
        # モード関連の初期化
        self.mode = EnemyMode.CHASE  # 初期モードは追跡
        self.mode_timer = time.time()  # モードタイマー
        self.chase_duration = 15  # 追跡モードの長さ
        self.territory_duration = 4  # 縄張りモードの長さ
        self.weak_duration = 10  # 弱体化モードの長さ
        self.weak_start_time = 0  # 弱体化開始時間
        self.is_eaten = False  # 食べられた状態
        
        self.territory_corners = [ # 縄張りモードの角
            (1, 1), 
            (1, map_data.height-2),
            (map_data.width-2, 1),
            (map_data.width-2, map_data.height-2)
        ]
        self.current_corner = self.enemy_id - 1 # 現在の縄張りの角

    def update(self) -> None:
        """敵の位置を更新"""
        current_time = time.time()
        
        # スタート時の遅延チェック
        if not self.can_move:
            if current_time - self.game_start_time >= self.start_delay:
                self.can_move = True
            else:
                return
        
        # 食べられた状態の処理
        if self.is_eaten:
            if not self.moving:
                self.current_path = self.find_path(self.get_grid_pos(), self.start_pos)
                if self.current_path:
                    self.moving = True
            self.move()
            if self.get_grid_pos() == self.start_pos:
                self.revive()
            return
        
        # 通常の状態更新
        if self.mode != EnemyMode.WEAK:
            if self.mode == EnemyMode.CHASE and current_time - self.mode_timer > self.chase_duration:
                self.mode = EnemyMode.TERRITORY
                self.mode_timer = current_time
            elif self.mode == EnemyMode.TERRITORY and current_time - self.mode_timer > self.territory_duration:
                self.mode = EnemyMode.CHASE
                self.mode_timer = current_time
        else:
            if current_time - self.weak_start_time > self.weak_duration:
                self.mode = EnemyMode.TERRITORY
                self.image = self.normal_image
                self.speed = self.default_speed
        
        if not self.moving:
            target = self.get_target_position()
            self.current_path = self.find_path(self.get_grid_pos(), target)
            if self.current_path:
                self.moving = True
        
        self.move()
        
        # プレイヤーとの衝突判定
        if pg.sprite.collide_rect(self, self.player):
            if self.mode == EnemyMode.WEAK and not self.is_eaten:
                self.get_eaten()
            elif self.mode != EnemyMode.WEAK and not self.is_eaten:
                # TODO: プレイヤーへのダメージ処理をここに実装
                pass

    def get_target_position(self) -> tuple[int, int]:
        """現在のモードに応じた目標位置を取得
        Returns:
            目標位置のグリッド座標(x, y)
        """
        if self.mode == EnemyMode.WEAK:
            return self.get_random_position()
        
        if self.mode == EnemyMode.TERRITORY:
            return self.territory_corners[self.current_corner]
        
        player_pos = self.player.get_grid_pos()
        if self.enemy_id == 1:
            return player_pos  # プレイヤーの現在のマス
        elif self.enemy_id == 2:
            return self.get_position_ahead(player_pos, 4)  # プレイヤーの進行方向の最大4マス先
        elif self.enemy_id == 3:
            return self.get_pincer_position()
        else:  # enemy_id == 4
            distance = self.calculate_distance(self.get_grid_pos(), player_pos)
            return player_pos if distance > 8 else self.get_random_position()

    def find_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list:
        """A*アルゴリズムによる経路探索
        Args:
            start: 開始位置のグリッド座標(x, y)
            goal: 目標位置のグリッド座標(x, y)
        Returns:
            経路のグリッド座標のリスト
        """
        def heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
            
            # 隣接マスの探索
            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # 経路の再構築
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        
        return path if len(path) > 1 else []

    def move(self) -> None:
        """現在の経路に沿って移動"""
        if not self.moving or not self.current_path:
            return
        
        # 現在の経路の次の目標地点を取得
        next_pos = self.current_path[0]
        target = get_pixel_pos(*next_pos)
        current = pg.math.Vector2(self.rect.center)
        target = pg.math.Vector2(target)
        
        # 現在位置から目標地点までのベクトルを計算
        direction = target - current
        distance = direction.length()
        
        if distance <= self.speed:
            # 目標地点に到達
            self.rect.center = target
            self.current_path.pop(0)
            if not self.current_path:
                self.moving = False
                if self.mode == 'TERRITORY':
                    self.current_corner = (self.current_corner + 1) % 4
        else:
            # 目標地点まで移動
            direction.scale_to_length(self.speed)
            self.rect.center = tuple(current + direction)

    def make_weak(self) -> None:
        """弱体化モードに移行"""
        if not self.is_eaten:
            self.mode = EnemyMode.WEAK
            self.weak_start_time = time.time()
            self.image = self.weak_image
            self.speed = self.default_speed * 0.8  # 速度を20%減少

    def get_eaten(self) -> None:
        """食べられた状態に移行"""
        self.is_eaten = True
        self.image = self.eaten_image
        self.speed = self.default_speed * 2  # 速度を2倍に上昇
        self.current_path = []
        self.moving = False

    def revive(self) -> None:
        """復活処理"""
        self.is_eaten = False
        self.image = self.normal_image
        self.speed = self.default_speed
        self.mode = EnemyMode.CHASE
        self.mode_timer = time.time()
        self.current_path = []
        self.moving = False

    def get_grid_pos(self) -> tuple[int, int]:
        """現在のグリッド座標を取得
        Returns:
            現在のグリッド座標(x, y)
        """
        return self.rect.centerx // GRID_SIZE, self.rect.centery // GRID_SIZE

    def get_neighbors(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """指定された位置の隣接する移動可能なグリッドを取得
        Args:
            pos: グリッド座標(x, y)
        Returns:
            隣接する移動可能なグリッド座標のリスト
        """
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.map_data.width and 
                0 <= ny < self.map_data.height and 
                self.map_data.playfield[ny][nx]['path']):
                neighbors.append((nx, ny))
        return neighbors

    def calculate_distance(self, pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        """2つのグリッド座標間のマンハッタン距離を計算
        Args:
            pos1: グリッド座標(x, y)
            pos2: グリッド座標(x, y)
        Returns:
            マンハッタン距離
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_position_ahead(self, pos: tuple[int, int], distance: int) -> tuple[int, int]:
        """プレイヤーの前方の位置を計算（壁を考慮）
        Args:
            pos: プレイヤーのグリッド座標(x, y)
            distance: 前方への距離
        Returns:
            計算されたグリッド座標(x, y)
        """
        dx = pos[0] - self.get_grid_pos()[0]
        dy = pos[1] - self.get_grid_pos()[1]
        
        if abs(dx) > abs(dy):
            # x方向の移動を優先
            for d in range(distance, 0, -1):
                new_x = pos[0] + (d if dx > 0 else -d)
                if (0 <= new_x < self.map_data.width and 
                    self.map_data.playfield[pos[1]][new_x]['path']):
                    return (new_x, pos[1])
        else:
            # y方向の移動を優先
            for d in range(distance, 0, -1):
                new_y = pos[1] + (d if dy > 0 else -d)
                if (0 <= new_y < self.map_data.height and 
                    self.map_data.playfield[new_y][pos[0]]['path']):
                    return (pos[0], new_y)
        return pos  # 移動可能な位置が見つからない場合は現在位置を返す

    def get_pincer_position(self) -> tuple[int, int]:
        """
        プレイヤーと別の敵を結ぶ線分の延長線上の位置を計算する。
        ただし、壁を考慮し、移動可能な範囲内で最も近い位置を返す。
        Returns:
            計算されたグリッド座標(x, y)
        """
        enemy1_pos = self.get_grid_pos()
        player_pos = self.player.get_grid_pos()
        dx = player_pos[0] - enemy1_pos[0]
        dy = player_pos[1] - enemy1_pos[1]
        
        target_x = enemy1_pos[0] + dx * 2
        target_y = enemy1_pos[1] + dy * 2
        
        # 目標位置が移動可能かチェック
        if (0 <= target_x < self.map_data.width and 
            0 <= target_y < self.map_data.height and 
            self.map_data.playfield[target_y][target_x]['path']):
            return (target_x, target_y)
        
        # 移動不可能な場合は、最も近い移動可能な位置を探す
        min_distance = float('inf')
        best_pos = enemy1_pos
        
        for y in range(max(0, target_y-2), min(self.map_data.height, target_y+3)):
            for x in range(max(0, target_x-2), min(self.map_data.width, target_x+3)):
                if self.map_data.playfield[y][x]['path']:
                    dist = abs(x - target_x) + abs(y - target_y)
                    if dist < min_distance:
                        min_distance = dist
                        best_pos = (x, y)
        
        return best_pos

    def get_random_position(self) -> tuple[int, int]:
        """ランダムな移動可能位置を取得（壁を考慮）
        Returns:
            ランダムな移動可能位置のグリッド座標(x, y)
        """
        valid_positions = []
        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                if self.map_data.playfield[y][x]['path']:
                    valid_positions.append((x, y))
        
        return random.choice(valid_positions) if valid_positions else self.get_grid_pos()
    

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


class DebugInfo:
    """デバッグ情報を表示するクラス"""
    def __init__(self, player: 'Player', enemies: pg.sprite.Group, baits: pg.sprite.Group) -> None:
        """初期化
        Args:
            player: プレイヤーオブジェクト
            enemies: 敵のスプライトグループ
            baits: エサのスプライトグループ
        """
        self.player = player
        self.enemies = enemies
        self.baits = baits
        self.font = pg.font.Font(None, 30)
        self.item_count = len(baits)
        self.items_eaten = 0
        self.enemy_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # 敵ごとの色

    def update(self):
        """デバッグ情報の更新"""
        self.items_eaten = self.item_count - len(self.baits)

    def draw(self, screen: pg.Surface):
        """デバッグ情報の描画
        Args:
            screen: 描画先のスクリーン
        """
        # プレイヤー情報の表示
        player_pos_text = self.font.render(f"Player Pos: {self.player.get_grid_pos()}", True, WHITE)
        screen.blit(player_pos_text, (WIDTH - 300, 20))
        player_moving_text = self.font.render(f"Moving: {self.player.moving}", True, WHITE)
        screen.blit(player_moving_text, (WIDTH - 300, 50))
        player_direction_text = self.font.render(f"Direction: {self.player.current_direction}", True, WHITE)
        screen.blit(player_direction_text, (WIDTH - 300, 80))

        # 敵の情報の表示と経路の描画
        for i, enemy in enumerate(self.enemies):
            enemy_info_text = self.font.render(f"Enemy {enemy.enemy_id}: {enemy.mode.name}", True, WHITE)
            screen.blit(enemy_info_text, (WIDTH - 300, 120 + i * 80))
            target_pos = enemy.get_target_position()
            target_rect = pg.Rect(get_pixel_pos(*target_pos), (10, 10))
            pg.draw.rect(screen, self.enemy_colors[i], target_rect)
            if enemy.current_path and len(enemy.current_path) >= 2:
                points = [get_pixel_pos(*pos) for pos in enemy.current_path]
                pg.draw.lines(screen, self.enemy_colors[i], False, points, 3)

        # アイテム情報の表示
        item_count_text = self.font.render(f"Total Items: {self.item_count}", True, WHITE)
        screen.blit(item_count_text, (WIDTH - 300, 450))
        items_eaten_text = self.font.render(f"Items Eaten: {self.items_eaten}", True, WHITE)
        screen.blit(items_eaten_text, (WIDTH - 300, 480))


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