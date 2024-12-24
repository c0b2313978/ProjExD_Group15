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
    def __init__(self, grid_pos: tuple[int, int], map_data: 'Map') -> None:
        """プレイヤーの初期化
        Args:
            grid_pos: グリッド座標(x, y)
            map_data: マップデータ
        """
        super().__init__()
        self.map_data = map_data

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
        screen.blit(self.image, self.rect)

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