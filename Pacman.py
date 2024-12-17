import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        self.state = "normal"
        self.hyper_life = 0
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        
        # 左Shiftキー押下時の高速化処理を追加
        if key_lst[pg.K_LSHIFT]:
            self.speed = 20
        else:
            self.speed = 10
        
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

        if self.state == "hyper":  # 無敵状態の処理の追加
            self.hyper_life -= 1
            if self.hyper_life <= 0:
                self.state = "normal"  # 無敵状態を解除
                self.image = self.image  # 通常画像に戻す
            else:
                self.image = pg.transform.laplacian(self.image)  # 特殊画像

        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle: float = 0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        base_angle = math.degrees(math.atan2(-self.vy, self.vx))
        angle += base_angle
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery + bird.rect.height * self.vy
        self.rect.centerx = bird.rect.centerx + bird.rect.width * self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class NeoBeam:
    def __init__(self, bird: Bird, num: int):
        """
        指定されたビーム数で弾幕を生成する
        引数 bird：ビームを発射するこうかとん
        引数 num：発射するビーム数
        """
        self.bird = bird
        self.num = num

    def gen_beams(self) -> list[Beam]:
        """
        指定されたビーム数のビームを生成し，リストで返す
        """
        # step = 50
        # angles = range(-50, 51, step)
        # return [Beam(self.bird, angle) for angle in angles]
        beams = []
        if self.num > 1 :
            step = 100 // (self.num -1)
            for i in range(self.num):
                angle = -50 + i * step
                beams.append(Beam(self.bird, angle))
        else:
            beams.append(Beam(self.bird))

        return beams


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(random.choice(__class__.imgs), 0, 0.8)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vx, self.vy = 0, +6
        self.bound = random.randint(50, HEIGHT//2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.move_ip(self.vx, self.vy)
    def inactivate(self):
        """
        敵機を無効化する
        """
        self.interval = float("inf")
        self.image = pg.transform.laplacian(self.image)


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 100
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)    


class EMP(pg.sprite.Sprite):
    """
    電磁パルス(EMP)に関するクラス
    """
    def __init__(self,emys:"pg.sprite.Group",bombs:"pg.sprite.Group",screen:pg.Surface):
        """
        EMPを生成する
        引数1 emys: 敵機グループ
        引数2 bombs: 爆弾グループ
        引数3 screen: 画面Surface
        """
        super().__init__()
        self.image = pg.Surface(((WIDTH,HEIGHT)))
        pg.draw.rect(self.image,(255,255,0),(0,0,WIDTH,HEIGHT)) #黄色で塗りつぶし
        self.image.set_alpha(100)  #半透明にする
        self.rect = self.image.get_rect()
        self.life =2  #接続時間(0.05秒 * 50fps = 2.5フレーム　＝　2フレーム)

        for emy in emys:
            emy.inactivate()  #敵機無効化
        for bomb in bombs:
            bomb.speed /= 2
            bomb.state = "inactive"  # 爆弾無効化

        screen.blit(self.image, self.rect)  # EMPエフェクト表示
        pg.display.update()
        time.sleep(0.05)  # 0.05秒ウェイト


class Gravity(pg.sprite.Sprite):
    """
    重力場に関するクラス
    """
    def __init__(self, life: int):
        """
        重力場を生成する
        引数:life (発動時間:400フレーム)
        """
        super().__init__()
        self.image = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        self.image.set_alpha(100)
        self.rect =  self.image.get_rect()
        self.life = life

    def update(self):
        """
        重力場の持続時間の管理
        0未満になったらkillする
        """
        self.life -= 1
        if self.life < 0:
            self.kill()


class Shield(pg.sprite.Sprite):
    """
    防御壁に関するクラス
    """
    def __init__(self, bird: Bird, life: int):
        """
        防御壁を生成する
        引数1 bird: こうかとんインスタンス
        引数2 life: 防御壁の持続時間（フレーム数）
        """
        super().__init__()
        self.bird = bird # こうかとんインスタンスを保持
        self.base_image = pg.Surface((20, bird.rect.height * 2)) # 回転前のSurfaceを保存
        pg.draw.rect(self.base_image, (0, 0, 255), (0, 0, 20, bird.rect.height * 2))  # 青い矩形を描画

        self.vx, self.vy = self.bird.dire # こうかとんの向きを取得
        angle = math.degrees(math.atan2(-self.vy, self.vx)) # 角度を計算
        self.image = pg.transform.rotate(self.base_image, angle) # base_imageを回転
        self.rect = self.image.get_rect()
        self.rect.centerx = self.bird.rect.centerx + self.bird.rect.width * self.vx
        self.rect.centery = self.bird.rect.centery + self.bird.rect.height * self.vy

        # self.update_position() # 初期位置設定
        self.life = life

    def update(self):
        """
        防御壁の持続時間を管理し、時間切れで消滅させる
        """
        # self.update_position() # こうかとんの位置に合わせて防御壁の位置を更新
        self.life -= 1
        if self.life < 0:
            self.kill()

    # def update_position(self):  # 追従可能にする
    #     """
    #     こうかとんの位置と向きに合わせて防御壁の位置と角度を更新する
    #     """
    #     self.vx, self.vy = self.bird.dire # こうかとんの向きを取得
    #     angle = math.degrees(math.atan2(-self.vy, self.vx)) # 角度を計算
    #     self.image = pg.transform.rotate(self.base_image, angle) # base_imageを回転
    #     self.rect = self.image.get_rect()
    #     self.rect.centerx = self.bird.rect.centerx + self.bird.rect.width * self.vx
    #     self.rect.centery = self.bird.rect.centery + self.bird.rect.height * self.vy


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()
    emps = pg.sprite.Group()  # EMPグループを追加
    gravities = pg.sprite.Group()
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()

    shields = pg.sprite.Group()  # Shieldグループを追加

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    beams.add(Beam(bird))
            if event.type == pg.KEYDOWN and event.key == pg.K_e and score.value >= 10:  # EMP発動
                score.value -= 10
                emps.add(EMP(emys, bombs, screen))
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and score.value >= 2:
                score.value -=2
                gravities.add(Gravity(400))

            if key_lst[pg.K_RSHIFT] and bird.state == "normal" and score.value >= 100:
                bird.state = "hyper"
                bird.hyper_life = 500
                score.value -= 100

            # sキー押下時、スコアが50以上、防御壁が存在しない場合
            if event.type == pg.KEYDOWN and event.key == pg.K_s and score.value >= 50 and len(shields) == 0:
                score.value -= 50
                shields.add(Shield(bird, 400))  # 防御壁を生成

            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if key_lst[pg.K_LSHIFT]: # 左Shiftキーが押されている場合
                    beams.add(NeoBeam(bird, 5).gen_beams()) # 5方向にビームを発射
                else:
                    beams.add(Beam(bird))
                        
        for gravity in gravities:
            for bomb in pg.sprite.spritecollide(gravity, bombs, True):
                exps.add(Explosion(bomb, 50))
                score.value += 1
            for emy in pg.sprite.spritecollide(gravity, emys, True):
                exps.add(Explosion(emy, 100))
                score.value += 10
                bird.change_img(6, screen)

        screen.blit(bg_img, [0, 0])

        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():  # ビームと衝突した敵機リスト
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():  # ビームと衝突した爆弾リスト
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ

        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            if bird.state == "hyper":
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.value += 1  # 1点アップ
            else:    
                bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return

        for bomb in pg.sprite.groupcollide(bombs, shields, True, False): # 爆弾と防御壁の衝突判定
            exps.add(Explosion(bomb, 50)) # 爆発エフェクト
            score.value += 1 # スコア加算

        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        emps.update()  #EMPを更新
        gravities.update()
        gravities.draw(screen)

        shields.update() # 防御壁を更新
        shields.draw(screen) # 防御壁を描画

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
