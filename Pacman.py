from enum import Enum, auto
import heapq
import os
import random
import sys
import time
import pygame as pg
import math


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
    """現在のグリッド座標を返す
    Args:
        pixel_x: ピクセルX座標
        pixel_y: ピクセルY座標
    Returns:
        現在のグリッド座標(x, y)
    """
    return pixel_x // GRID_SIZE, pixel_y // GRID_SIZE


def get_pixel_pos(grid_x: int, grid_y: int) -> tuple[int, int]:
    """グリッド座標からピクセル座標を計算して返す
    Args:
        grid_x: グリッドX座標
        grid_y: グリッドY座標
    Returns:
        ピクセル座標(x, y)
    """
    pixel_x = grid_x * GRID_SIZE + GRID_SIZE // 2
    pixel_y = grid_y * GRID_SIZE + GRID_SIZE // 2
    return pixel_x, pixel_y


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
            4: (255, 192, 203), # ゴーストの家の入り口: ピンク
            5: (0, 255, 0)     # ワープトンネル: 緑
        }
        
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                rect_x = field_start[0] + (x * GRID_SIZE)
                rect_y = field_start[1] + (y * GRID_SIZE)
                
                if cell in colors:
                    pg.draw.rect(screen, colors[cell], (rect_x, rect_y, GRID_SIZE, GRID_SIZE))


class Player(pg.sprite.Sprite):
    def __init__(self, grid_pos: tuple[int, int], map_data: Map):
        super().__init__()
        self.grid_pos = grid_pos
        self.map_data = map_data
        self.lives = 3  # 残機の初期値
        self.font = pg.font.Font(None, 30)

        # 画像関連の初期化
        self.original_images = [
            pg.transform.scale(pg.image.load("fig/pac-man1.png").convert_alpha(), (PLAYER_SIZE, PLAYER_SIZE)),
            pg.transform.scale(pg.image.load("fig/pac-man2.png").convert_alpha(), (PLAYER_SIZE, PLAYER_SIZE))
        ]
        self.current_frame = 0  # 現在のアニメーションフレーム
        self.animation_counter = 0  # アニメーション用カウンター
        self.animation_speed = 5
        self.image = self.original_images[0]
        self.rect = self.image.get_rect()  # rect属性を初期化

        # 位置関連
        self.rect.center = get_pixel_pos(*grid_pos)  # 初期位置を設定
        self.target_pos = self.rect.center
        self.moving = False

        # 移動関連
        self.current_direction = None  # 現在の移動方向
        self.queued_direction = None  # 次の曲がり角で進みたい方向

        # 回転関連
        self.angle = 0  # 現在の角度
        self.target_angle = 0  # 目標の角度
        self.rotation_speed = 45  # 回転速度

        # ワープ関連の変数
        self.can_warp = True  # ワープ可能かどうかのフラグ
        self.last_warp_pos = None  # 最後にワープした位置
        self.warp_cells = [tuple(cell.values()) for cell in map_data.tunnels]

    def reset_position(self): 
        """
        プレイヤーの位置を初期位置に戻す
        """
        self.rect.center = get_pixel_pos(*self.grid_pos)  # 初期位置に設定
        self.current_direction = None  # 移動方向をリセット
        self.moving = False
        
        

        

    
    def handle_input(self, keys: pg.key.ScancodeWrapper) -> None:
        """キー入力を処理
        Args:
            keys: キー入力の状態
        """
        new_direction = None
        
        # 新しい入力方向を取得
        if keys[pg.K_LEFT]:
            new_direction = (-1, 0)
        elif keys[pg.K_RIGHT]:
            new_direction = (1, 0)
        elif keys[pg.K_UP]:
            new_direction = (0, -1)
        elif keys[pg.K_DOWN]:
            new_direction = (0, 1)
        
        # 新しい入力があれば保存
        if new_direction:
            self.queued_direction = new_direction
            
            # 移動中でなければ、即座に移動を試みる
            # 移動中なら、updateメソッドで次の交差点に到達した時に方向転換を試みる
            if not self.moving:
                self.try_move(new_direction)
    
    def try_move(self, direction: tuple[int, int]) -> bool:
        """指定された方向への移動を試みる。移動可能であれば移動処理を行いTrueを返す。
        Args:
            direction: 移動方向(x, y)
        Returns:
            移動可能であればTrue, そうでなければFalse
        """
        current_pos = self.get_grid_pos()  # 現在のグリッド座標を取得
        next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])  # 次のグリッド座標を計算

        if not self.is_valid_move(next_pos):  # 次の座標が移動可能か確認
            return False

        # ワープトンネルの処理
        if self.map_data.playfield[next_pos[1]][next_pos[0]]['tunnel'] and self.can_warp:
            warp_pos = self.get_warp_destination(next_pos)  # ワープ先の座標を取得
            if warp_pos:
                self.rect.center = get_pixel_pos(*warp_pos)  # プレイヤーをワープ
                self.target_pos = self.rect.center  # 目標位置を更新
                self.last_warp_pos = warp_pos  # 最後にワープした位置を記録
                self.can_warp = False

                next_pos = (warp_pos[0] + direction[0], warp_pos[1] + direction[1])  # ワープ後の次の移動先を計算
                if not self.is_valid_move(next_pos):  # ワープ後の移動先が有効か確認
                    return False

        self.current_direction = direction  # 移動方向を更新
        self.target_pos = get_pixel_pos(*next_pos)  # 目標位置を更新
        self.moving = True
        self.update_rotation(direction)  # プレイヤーの回転を更新
        return True  # 移動処理が完了したのでTrueを返す

    def update_rotation(self, direction: tuple[int, int]) -> None:
        """移動方向に応じて回転角度を設定
        Args:
            direction: 移動方向(x, y)
        """
        new_angle = 0
        if direction[0] > 0:
            new_angle = 0  # 右
        elif direction[0] < 0:
            new_angle = 180  # 左
        elif direction[1] > 0:
            new_angle = 90  # 下
        elif direction[1] < 0:
            new_angle = 270  # 上
        
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
        """ワープ先の座標を取得
        Args:
            current_pos: 現在のグリッド座標(x, y)
        Returns:
            ワープ先のグリッド座標(x, y), ワープ先がない場合はNone
        """
        if self.last_warp_pos == current_pos:
            return None
        
        # 現在位置以外のワープトンネルを探す
        for cell in self.warp_cells:
            if cell != current_pos and cell != self.last_warp_pos:
                return cell
        return None

    def update(self) -> None:
        """プレイヤーの位置を更新"""
        if self.moving:
            # 目標位置に到達したかチェック
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            
            if abs(dx) <= PLAYER_SPEED and abs(dy) <= PLAYER_SPEED:
                self.rect.center = self.target_pos
                self.moving = False

                # 次の移動を処理
                if self.queued_direction:
                    # まず待機中の方向に移動を試みる
                    if not self.try_move(self.queued_direction):
                        # できない場合は現在の方向に継続
                        if self.current_direction:
                            self.try_move(self.current_direction)
                elif self.current_direction:
                    # 待機方向がない場合は現在の方向に継続
                    self.try_move(self.current_direction)

                # 移動完了時にワープ可能フラグを更新
                current_pos = self.get_grid_pos()
                if not self.is_tunnel_position(current_pos):
                    self.can_warp = True
                    self.last_warp_pos = None

            else:
                # 移動を継続
                move_x = PLAYER_SPEED * (1 if dx > 0 else -1 if dx < 0 else 0)  # 目標位置が右にあれば正の速度、左にあれば負の速度、同じなら0
                move_y = PLAYER_SPEED * (1 if dy > 0 else -1 if dy < 0 else 0)  # 目標位置が下にあれば正の速度、上にあれば負の速度、同じなら0
                self.rect.centerx += move_x
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
        # プレイヤーの画像を描画
        screen.blit(self.image, self.rect)

    # 残機数を描画
        lives_text = self.font.render(f"Life: {self.lives}", True, (255, 255, 255))  # 白色のテキスト
        screen.blit(lives_text, (20, 0))  # 左上の座標(20, 20)に描画

    def get_grid_pos(self) -> tuple[int, int]:
        """現在のグリッド座標を取得
        Returns:
            現在のグリッド座標(x, y)
        """
        return (self.rect.centerx // GRID_SIZE, self.rect.centery // GRID_SIZE)
    
    def is_tunnel_position(self, pos: tuple[int, int]) -> bool:
        """指定された位置がワープトンネルかどうかを判定
        Args:
            pos: グリッド座標(x, y)
        Returns:
            ワープトンネルであればTrue, そうでなければFalse
        """
        x, y = pos
        return self.map_data.playfield[y][x]['tunnel']
    
    # def game_over(screen: pg.Surface):
    #     """
    #     ゲームオーバー画面を表示
    #     """
    #     font = pg.font.Font(None, 60)
    #     game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    #     retry_text = font.render("Press R to Retry or Q to Quit", True, WHITE)

    #     screen.fill((0, 0, 0))
    #     screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    #     screen.blit(retry_text, (WIDTH // 2 - 200, HEIGHT // 2 + 20))
    #     pg.display.update()

    #     while True:
    #         for event in pg.event.get():
    #             if event.type == pg.QUIT:
    #                 pg.quit()
    #                 sys.exit()
    #             if event.type == pg.KEYDOWN:
    #                 if event.key == pg.K_r:
    #                     main()  # ゲームを再スタート
    #                 if event.key == pg.K_q:
    #                     pg.quit()
    #                     sys.exit()



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

        image_idex = [0, 4, 5, 7]
        
        # 画像の読み込みとスケーリング
        self.normal_image_base = pg.transform.scale(
            pg.image.load(f"fig/{image_idex[enemy_id-1]}.png").convert_alpha(), 
            (ENEMY_SIZE, ENEMY_SIZE)
        )
        self.normal_image_lst = {
            (-1, 0): self.normal_image_base,  # 左向き
            (1, 0): pg.transform.flip(self.normal_image_base, True, False),  #右向き
            (0, -1): self.normal_image_base,  # 上向き
            # (0, -1): pg.transform.rotozoom(self.normal_image_base, -90, 1),  # 上向き
            (0, 1): pg.transform.rotozoom(self.normal_image_base, 90, 1)}  # 下向き
        self.normal_image = self.normal_image_lst[(1, 0)]

        self.weak_images = [
            pg.transform.scale(pg.image.load("fig/chicken.png").convert_alpha(), (ENEMY_SIZE, ENEMY_SIZE)),
            pg.transform.scale(pg.image.load("fig/food_christmas_chicken.png").convert_alpha(), (ENEMY_SIZE, ENEMY_SIZE)),
            pg.transform.scale(pg.image.load("fig/chicken_honetsuki.png").convert_alpha(), (ENEMY_SIZE, ENEMY_SIZE)),
            ]
        self.current_weak_image = None  # 現在選択中のweak画像

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
                self.player.reset_position()  # プレイヤーへのダメージ処理をここに実装
                self.player.lives -= 1

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
        
        # 移動方向に応じて画像を更新
        if not self.is_eaten and self.mode != EnemyMode.WEAK:
            dx = 1 if direction.x > 0 else -1 if direction.x < 0 else 0
            dy = 1 if direction.y > 0 else -1 if direction.y < 0 else 0
            
            # x方向の移動が y方向より大きい場合
            if abs(direction.x) > abs(direction.y):
                direction_key = (dx, 0)
            else:
                direction_key = (0, dy)
                
            if direction_key in self.normal_image_lst:
                self.normal_image = self.normal_image_lst[direction_key]
                self.image = self.normal_image

    def make_weak(self) -> None:
        """弱体化モードに移行"""
        if not self.is_eaten:
            self.mode = EnemyMode.WEAK
            self.weak_start_time = time.time()
            # まだweak画像が選択されていない場合のみ、ランダムに選択
            if self.current_weak_image is None:
                self.current_weak_image = random.choice(self.weak_images)
            self.image = self.current_weak_image
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
        self.current_weak_image = None  # weak画像の選択をリセット

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
    """アイテム（エサ）の管理クラス"""
    def __init__(self, grid_pos: tuple[int, int], item_type: int, score: 'Score') -> None:
        """アイテムの初期化
        Args:
            grid_pos: グリッド座標(x, y)
            item_type: アイテムの種類 (1: 通常エサ, 2: パワーエサ)
        """
        super().__init__()
        self.image = pg.Surface((GRID_SIZE, GRID_SIZE), pg.SRCALPHA)
        self.grid_pos = grid_pos
        self.item_type = item_type
        self.score = score
        self.eat_count = 0
        
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
            self.score.value += 20  # エサを食べたらscore+20
            self.kill()
            self.eat_count += 1


class Score:
    """
    コインを獲得したときスコアとして表示するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 40)  # サイズは40
        self.color = (255, 255, 255)  # カラーは白
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH - 110, HEIGHT - 50

    def draw(self, screen: pg.Surface):  
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

    # タイトル表示(画面上部に配置)
    font_title = pg.font.Font(None, 100)
    title_text = font_title.render("PacmanGame", True, (255, 255, 0))  # 黄色の文字
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))  # 上部（y=50）に配置
     
    # パックマンのイラストを描画
    pacman_center = (WIDTH // 2, HEIGHT // 2 - 50)
    pacman_radius = 100
    pacman_color = (255, 255, 0)  # 黄色
    pacman_mouth_angle = 30  # 口の開き角度

    # パックマン本体の描画（扇形）
    points = [pacman_center]
    for angle in range(pacman_mouth_angle, 360 - pacman_mouth_angle + 1, 1): 
        x = pacman_center[0] + pacman_radius * math.cos(math.radians(angle))
        y = pacman_center[1] - pacman_radius * math.sin(math.radians(angle))
        points.append((x, y))
    pg.draw.polygon(screen, pacman_color, points)

    # パックマンの目を描画
    eye_position = (pacman_center[0] + pacman_radius // 4, pacman_center[1] - pacman_radius // 2)
    eye_radius = 10
    pg.draw.circle(screen, (0, 0, 0), eye_position, eye_radius)

    # ------------------------------------------------
    # ここから “Select Difficulty” と難易度別テキスト
    # ------------------------------------------------

    font_subtitle = pg.font.Font(None, 50)
    
    # 「Select Difficulty」 のテキストを描画
    select_diff_text = font_subtitle.render("PRESS KEY", True, (255, 255, 255))  # 白色で描画
    # 難易度テキスト群より少し上に置きたいので、この時点ではまだ座標を決めずにおく
    
    # それぞれ色を変えて render する
    press_key_text = font_subtitle.render("Select Difficulty ", True, (255, 255, 255))  # 白
    easy_text      = font_subtitle.render("1: Easy ",   True, (  0, 255,   0))  # 緑
    normal_text    = font_subtitle.render("2: Normal ", True, (255, 255,   0))  # 黄
    hard_text      = font_subtitle.render("3: Hard",    True, (255,   0,   0))  # 赤

    # 全パーツの横幅合計を計算 → 中央寄せのためのX座標を求める
    difficulty_line_total_width = (
        press_key_text.get_width() + 
        easy_text.get_width()      + 
        normal_text.get_width()    + 
        hard_text.get_width()
    )
    start_x = WIDTH // 2 - difficulty_line_total_width // 2

    # “Select Difficulty” の表示幅を用いて、それも中央寄せ
    select_diff_x = WIDTH // 2 - select_diff_text.get_width() // 2
    
    # 配置するY座標を決める
    # まず Select Difficulty を表示し、その少し下に難易度行を表示する
    select_diff_y = HEIGHT // 2 + 50 + 50  # 例えば画面の中央から50px下
    difficulty_line_y = select_diff_y + 60  # 例えば “select difficulty” の下に 60px

    # “Select Difficulty” を描画
    screen.blit(select_diff_text, (select_diff_x, select_diff_y))

    # 難易度別テキストを一行にまとめて表示
    x = start_x
    screen.blit(press_key_text, (x, difficulty_line_y))
    x += press_key_text.get_width()
    screen.blit(easy_text, (x, difficulty_line_y))
    x += easy_text.get_width()
    screen.blit(normal_text, (x, difficulty_line_y))
    x += normal_text.get_width()
    screen.blit(hard_text, (x, difficulty_line_y))

    # ------------------------------------------------
    # コピーライト表示
    # ------------------------------------------------
    font_copyright = pg.font.Font(None, 30)
    copyright_text = font_copyright.render("(c) 2024 Group15", True, (255, 255, 255))
    screen.blit(
        copyright_text,
        (WIDTH - copyright_text.get_width() - 10, HEIGHT - copyright_text.get_height() - 10)
    )


def draw_game_over(screen):
    """
    ゲームオーバー画面を描画する関数
    """
    font=pg.font.Font(None,74)
    game_text=font.render("GAME",True,WHITE)
    over_text=font.render("OVER",True,WHITE)

    screen_center_x=WIDTH//2
    screen_center_y=HEIGHT//2

    game_rect = game_text.get_rect(centerx=screen_center_x, centery=screen_center_y - 50)
    over_rect = over_text.get_rect(centerx=screen_center_x, centery=screen_center_y + 50)
    
    screen.blit(game_text, game_rect)
    screen.blit(over_text, over_rect)
    
    # パックマンの画像を"GAME"と"OVER"の間に描画
    pacman_image = pg.transform.scale(pg.image.load("fig/pac-man1.png").convert_alpha(), (50, 50))
    pacman_rect = pacman_image.get_rect(center=(screen_center_x, screen_center_y))
    screen.blit(pacman_image, pacman_rect)
    

def input_map_data(map_n):
    """
    マップデータを入力して返す関数
    """
    map_dic = {1: "map1.txt", 2: "map2.txt", 3: "map3.txt"}
    map_data = Map(map_dic[map_n])
    player = Player((1, 1), map_data)
    score = Score()
    # エサんｐグループを作成
    baits = pg.sprite.Group()
    for x in range(map_data.height):
        for y in range(map_data.width):
            if map_data.playfield[x][y]["dot"] in [1, 2]:
                baits.add(Item((y, x), map_data.playfield[x][y]["dot"], score))

    # 敵のグループを作成
    enemies = pg.sprite.Group()
    for i in range(4):
        enemies.add(Enemy(i+1, player, map_data))

    # デバッグ情報表示クラスのインスタンスを作成
    debug_info = DebugInfo(player, enemies, baits)
    return map_data, player, score, baits, enemies, debug_info


def main():
    pg.display.set_caption("Pacman")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    start = True  

    tmr = 0
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        if start:
            draw_start_screen(screen)  # スタート画面を描画
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_1:  # スペースキーで開始 難易度：低い
                    start = False
                    map_data, player, score, baits, enemies, debug_info = input_map_data(2)

                if event.type == pg.KEYDOWN and event.key == pg.K_2:  # スペースキーで開始 難易度：普通
                    start = False
                    map_data, player, score, baits, enemies, debug_info = input_map_data(3)
                    
                if event.type == pg.KEYDOWN and event.key == pg.K_3:  # スペースキーで開始 難易度：高い
                    start = False
                    map_data, player, score, baits, enemies, debug_info = input_map_data(1)
        else:
            screen.fill((0, 0, 0))
            # マップの描画
            # map_data.draw(screen, (WIDTH//2 - map_data.width*GRID_SIZE//2, HEIGHT//2 - map_data.height*GRID_SIZE//2))
            map_data.draw(screen, (0, 0))

            baits.draw(screen)
            baits.update(player)

            # プレイヤーの更新と描画
            keys = pg.key.get_pressed()
            player.handle_input(keys)
            player.update()
            player.draw(screen)

            # 敵の更新と描画
            enemies.update()
            enemies.draw(screen)

            # # デバッグ情報の更新と描画
            # debug_info.update()
            # debug_info.draw(screen)

            # スコアの描画
            score.draw(screen)

            # パワーエサの処理
            for bait in baits:
                if bait.item_type == 2 and pg.sprite.collide_rect(player, bait):
                    for enemy in enemies:
                        enemy.make_weak()

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()