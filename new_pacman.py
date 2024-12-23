from enum import Enum, auto
import heapq
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 640  # ゲームウィンドウの高さ
GRID_SIZE = 20
PLAYER_SPEED = 3
PLAYER_SIZE = 20
ENEMY_SIZE = 30

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_grid_pos(pixel_x: int, pixel_y: int) -> tuple[int, int]:
    """現在のグリッド座標を返す"""
    return pixel_x // GRID_SIZE, pixel_y // GRID_SIZE


def get_pixel_pos(grid_x: int, grid_y: int) -> tuple[int, int]:
    """グリッド座標からピクセル座標を計算して返す"""
    pixel_x = grid_x * GRID_SIZE + GRID_SIZE // 2
    pixel_y = grid_y * GRID_SIZE + GRID_SIZE // 2
    return pixel_x, pixel_y


class Player(pg.sprite.Sprite):
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, grid_pos: tuple[int, int], map_data: 'Map') -> None:
        """プレイヤーの初期化
        Args:
            grid_pos: グリッド座標(x, y)
            map_data: マップデータ
        """
        super().__init__()
        self.map_data = map_data

        self.original_images = [
            pg.transform.scale(pg.image.load("fig/pac-man1.png").convert_alpha(), (PLAYER_SIZE, PLAYER_SIZE)),
            pg.transform.scale(pg.image.load("fig/pac-man2.png").convert_alpha(), (PLAYER_SIZE, PLAYER_SIZE))
        ]
        self.current_frame = 0  # 現在のアニメーションフレーム
        self.animation_counter = 0  # アニメーション用カウンター
        self.animation_speed = 5
        self.image = self.original_images[0]
        self.rect = self.image.get_rect()  # rect属性を初期化

        self.rect.center = get_pixel_pos(*grid_pos)  # 初期位置を設定
        self.target_pos = self.rect.center
        self.moving = False
        self.angle = 0  # 現在の角度
        self.target_angle = 0  # 目標の角度
        self.rotation_speed = 30  # 回転速度

        # ワープ関連の変数を追加
        self.can_warp = True  # ワープ可能かどうかのフラグ
        self.last_warp_pos = None  # 最後にワープした位置
        self.warp_cells = [tuple(cell.values()) for cell in map_data.tunnels]
    
    def move_to_grid(self, grid_pos: tuple[int, int]) -> None:
        """指定されたグリッド座標へ移動を開始
        
        Args:
            grid_pos: 移動先のグリッド座標(x, y)
        """
        if not self.moving and self.is_valid_move(grid_pos):
            # 現在の移動方向を保存（ワープ時の向き維持用）
            dx = grid_pos[0] - self.get_grid_pos()[0]
            dy = grid_pos[1] - self.get_grid_pos()[1]
            current_direction = (dx, dy)
            
            # ワープトンネルの処理
            if self.map_data.playfield[grid_pos[1]][grid_pos[0]]['tunnel'] and self.can_warp:
                warp_pos = self.get_warp_destination(grid_pos)
                if warp_pos:
                    # 瞬時にワープ
                    self.rect.center = get_pixel_pos(*warp_pos)
                    self.target_pos = self.rect.center
                    self.last_warp_pos = warp_pos
                    self.can_warp = False
                    
                    # ワープ後の次の移動先を設定
                    next_x = warp_pos[0] + current_direction[0]
                    next_y = warp_pos[1] + current_direction[1]
                    if self.is_valid_move((next_x, next_y)):
                        grid_pos = (next_x, next_y)
                    else:
                        return
            
            self.target_pos = get_pixel_pos(*grid_pos)
            self.moving = True
            
            # 移動方向に応じて角度を設定（ワープ時は向きを変えない）
            if not (self.map_data.playfield[grid_pos[1]][grid_pos[0]]['tunnel'] and self.can_warp):
                new_angle = 0
                if dx > 0:
                    new_angle = 0  # 右
                elif dx < 0:
                    new_angle = 180  # 左
                elif dy > 0:
                    new_angle = 90  # 下
                elif dy < 0:
                    new_angle = 270  # 上
                
                # 角度の差分を計算
                angle_diff = (new_angle - self.angle) % 360
                if abs(angle_diff) == 180:
                    self.angle = new_angle
                    self.target_angle = new_angle
                else:
                    if angle_diff > 180:
                        angle_diff -= 360
                    self.target_angle = self.angle + angle_diff

    def is_valid_move(self, grid_pos: tuple[int, int]) -> bool:
        """指定されたグリッド座標が移動可能か判定
        Args:
            grid_pos: 判定するグリッド座標(x, y)
        Returns:
            移動可能であればTrue, そうでなければFalse
        """
        grid_x, grid_y = grid_pos
        return self.map_data.playfield[grid_y][grid_x]['path']
    
    def get_warp_destination(self, current_pos: tuple[int, int]) -> tuple[int, int]:
        """ワープ先の座標を取得"""
        if self.last_warp_pos == current_pos:
            return None
        
        # 現在位置以外のワープトンネルを探す
        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                if (self.map_data.playfield[y][x]['tunnel'] and 
                    (x, y) != current_pos and 
                    (x, y) != self.last_warp_pos):
                    return (x, y)
        return None

    def update(self) -> None:
        """プレイヤーの位置を更新"""
        if self.moving:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            
            if abs(dx) <= PLAYER_SPEED and abs(dy) <= PLAYER_SPEED:
                self.rect.center = self.target_pos
                self.moving = False

                # 移動完了時にワープ可能フラグを更新
                current_pos = self.get_grid_pos()
                if not self.is_tunnel_position(current_pos):
                    self.can_warp = True
                    self.last_warp_pos = None

            else:
                move_x = PLAYER_SPEED if dx > 0 else -PLAYER_SPEED
                move_y = PLAYER_SPEED if dy > 0 else -PLAYER_SPEED
                
                if dx != 0:
                    self.rect.centerx += move_x
                if dy != 0:
                    self.rect.centery += move_y
        
        # 角度を更新
        if self.angle != self.target_angle:
            angle_diff = self.target_angle - self.angle
            if abs(angle_diff) <= self.rotation_speed:
                self.angle = self.target_angle
            else:
                self.angle += self.rotation_speed if angle_diff > 0 else -self.rotation_speed
        
        # アニメーションを更新
        self.update_animation()
        
        # 現在の角度に基づいて画像を回転
        self.image = pg.transform.rotate(self.original_images[self.current_frame], -self.angle)
    
    def update_animation(self) -> None:
        """アニメーションフレームを更新"""
        if self.moving:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed: # アニメーション速度調整
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % 2
        else:
            self.current_frame = 0
            self.animation_counter = 0
    
    def draw(self, screen: pg.Surface) -> None:
        """プレイヤーを描画
        Args:
            screen: 描画先のスクリーン
        """
        screen.blit(self.image, self.rect)

    def get_grid_pos(self) -> tuple[int, int]:
        """現在のグリッド座標を取得
        Returns:
            現在のグリッド座標(x, y)
        """
        return (self.rect.centerx // GRID_SIZE, self.rect.centery // GRID_SIZE)
    
    def is_tunnel_position(self, pos: tuple[int, int]) -> bool:
        """指定された位置がワープトンネルかどうかを判定"""
        x, y = pos
        return self.map_data.playfield[y][x]['tunnel']

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
        self.start_delay = enemy_id * 1  # 1秒ごとに順番にスタート
        self.game_start_time = time.time()
        self.can_move = False
        
        # モード関連の初期化
        self.mode = EnemyMode.TERRITORY
        self.mode_timer = time.time()
        self.chase_duration = 10
        self.territory_duration = 8
        self.weak_duration = 10
        self.weak_start_time = 0
        self.is_eaten = False  # 食べられた状態を追加
        
        self.territory_corners = [
            (1, 1), 
            (1, map_data.height-2),
            (map_data.width-2, 1),
            (map_data.width-2, map_data.height-2)
        ]
        self.current_corner = self.enemy_id - 1

    def update(self) -> None:
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
        """現在のモードに応じた目標位置を取得"""
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
        """A*アルゴリズムによる経路探索"""
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
        """現在のグリッド座標を取得"""
        return self.rect.centerx // GRID_SIZE, self.rect.centery // GRID_SIZE

    def get_neighbors(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """指定された位置の隣接する移動可能なグリッドを取得"""
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
        """2つのグリッド座標間のマンハッタン距離を計算"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_position_ahead(self, pos: tuple[int, int], distance: int) -> tuple[int, int]:
        """プレイヤーの前方の位置を計算（壁を考慮）"""
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
        """ランダムな移動可能位置を取得（壁を考慮）"""
        valid_positions = []
        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                if self.map_data.playfield[y][x]['path']:
                    valid_positions.append((x, y))
        
        return random.choice(valid_positions) if valid_positions else self.get_grid_pos()


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
            1: (33, 33, 255),  # 壁: 青
            4: (255, 192, 203) # ゴーストの家の入り口: ピンク
        }
        
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                rect_x = field_start[0] + (x * GRID_SIZE)
                rect_y = field_start[1] + (y * GRID_SIZE)
                
                if cell in colors:
                    pg.draw.rect(screen, colors[cell], (rect_x, rect_y, GRID_SIZE, GRID_SIZE))



class Item(pg.sprite.Sprite):
    """アイテム（エサ）の管理クラス"""
    def __init__(self, grid_pos: tuple[int, int], item_type: int) -> None:
        """アイテムの初期化
        Args:
            grid_pos: グリッド座標(x, y)
            item_type: アイテムの種類 (1: 通常エサ, 2: パワーエサ)
        """
        super().__init__()
        self.image = pg.Surface((GRID_SIZE, GRID_SIZE), pg.SRCALPHA)
        self.grid_pos = grid_pos
        self.item_type = item_type
        
        center_x = GRID_SIZE // 2
        center_y = GRID_SIZE // 2

        if self.item_type == 1: # 通常エサ
            self.color = (255, 105, 180) # ピンク
            self.radius = 3
            pg.draw.circle(self.image, self.color, (center_x, center_y), self.radius)

        elif self.item_type == 2: # パワーエサ
            self.color = (255, 105, 180) # ピンク
            self.radius = 6
            pg.draw.circle(self.image, self.color, (center_x, center_y), self.radius)
        
        self.rect = self.image.get_rect(center=get_pixel_pos(*grid_pos))
    
    def update(self, player: 'Player'):
        """
        アイテムを更新する
        プレイヤーと衝突したらkillする
        """
        if pg.sprite.collide_rect(self, player):
            self.kill()



def main():
    pg.display.set_caption("Pacman")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    map_data = Map("map2.txt")
    player = Player((1, 1), map_data)  

    # エサんｐグループを作成
    baits = pg.sprite.Group()
    for x in range(map_data.height):
        for y in range(map_data.width):
            if map_data.playfield[x][y]["dot"] in [1, 2]:
                baits.add(Item((y, x), map_data.playfield[x][y]["dot"]))

    # 敵のグループを作成
    enemies = pg.sprite.Group()
    for i in range(4):
        enemies.add(Enemy(i+1, player, map_data))

    tmr = 0
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        screen.fill((0, 0, 0))
        # マップの描画
        # map_data.draw(screen, (WIDTH//2 - map_data.width*GRID_SIZE//2, HEIGHT//2 - map_data.height*GRID_SIZE//2))
        map_data.draw(screen, (0, 0))

        # エサの描画と更新
        baits.draw(screen)
        baits.update(player)

        # プレイヤーの更新と描画
        keys = pg.key.get_pressed()
        if not player.moving:
            current_x, current_y = player.get_grid_pos()
            if keys[pg.K_LEFT]:
                player.move_to_grid((current_x - 1, current_y))
            elif keys[pg.K_RIGHT]:
                player.move_to_grid((current_x + 1, current_y))
            elif keys[pg.K_UP]:
                player.move_to_grid((current_x, current_y - 1))
            elif keys[pg.K_DOWN]:
                player.move_to_grid((current_x, current_y + 1))
        
        player.update()
        player.draw(screen)

        # 敵の更新と描画
        enemies.update()
        enemies.draw(screen)

        # パワーエサの処理
        for bait in baits:
            if bait.item_type == 2 and pg.sprite.collide_rect(player, bait):
                for enemy in enemies:
                    enemy.make_weak()
                bait.kill()



        pg.display.update()
        tmr += 1
        clock.tick(50)




if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()