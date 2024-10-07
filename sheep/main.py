import pgzrun
import pygame
import random

# 定义倒计时时间（秒）
COUNTDOWN_TIME_HARD = 60
COUNTDOWN_TIME_EASY = 90

pygame.init()

# 定义一个自定义事件
TIMER_EVENT = pygame.USEREVENT + 1

# 初始化倒计时
time_left = 0

# 定义游戏相关属性
TITLE = 'game'
WIDTH = 600
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH*7, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []

# 游戏状态
game_started = False
easy_mode = False
game_over_flag = False

# 计分
score = 0

# 鼠标位置
mouse_pos = (0, 0)

def initialize_game():
    global tiles, docks, time_left, score, game_over_flag
    tiles = []
    docks = []
    score = 0
    game_over_flag = False
    time_left = COUNTDOWN_TIME_EASY if easy_mode else COUNTDOWN_TIME_HARD

    # 初始化牌组，根据难度模式设置牌的数量
    if easy_mode:
        ts = list(range(1, 7)) * 6  # 低难度模式，6*6张牌
    else:
        ts = list(range(1, 13)) * 12  # 高难度模式，12*12张牌

    random.shuffle(ts)
    n = 0
    layers = 4 if easy_mode else 7  # 根据难度模式设置层数
    for k in range(layers):  # 层数
        for i in range(layers - k):  # 每层减1行
            for j in range(layers - k):
                t = ts[n]  # 获取排种类
                n += 1
                tile = Actor(f'tile{t}')  # 使用tileX图片创建Actor对象
                tile.pos = 120 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9  # 设定位置
                tile.tag = t  # 记录种类
                tile.layer = k  # 记录层级
                tile.status = 1 if k == (layers - 1) else 0  # 除了最顶层，状态都设置为0（不可点）这里是个简化实现
                tiles.append(tile)
    extra_tiles = 2 if easy_mode else 4  # 根据难度模式设置额外的牌数量
    for i in range(extra_tiles):  # 剩余的牌放下面（为了凑整能通关）
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        tile.pos = 210 + i * tile.width, 516
        tile.tag = t
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

    # 设置倒计时事件，每秒触发一次
    pygame.time.set_timer(TIMER_EVENT, 1000)

def update(dt):
    global time_left, game_over_flag
    mouse_pos = pygame.mouse.get_pos()
    if game_started and not game_over_flag:
        time_left -= dt
        if time_left <= 0:  # 时间用完则游戏失败
            game_over_flag = True
            game_over()

def game_over():
    screen.blit('end', (0, 0))

def draw_time():
    # 在屏幕上显示剩余时间
    screen.draw.text(f"Time left: {int(time_left)}", (10, 10), color="white")
    if int(time_left)==0:
        game_over()
        
def draw_score():
    # 在屏幕上显示分数
    screen.draw.text(f"Score: {score}", (10, 40), color="white")

# 游戏帧绘制函数
def draw():
    screen.clear()
    screen.blit('menubackground.png', (0, 0))  # 绘制背景图像
    if not game_started:
        # 绘制标题
        screen.draw.text("Game", center=(WIDTH // 2, 200), fontsize=200, color="white")
        
        # 绘制低难度按钮背景和文字
        easy_button_rect = Rect((WIDTH // 2 - 150, 350), (300, 100))
        easy_color = "white" if easy_button_rect.collidepoint(mouse_pos) else "green"
        screen.draw.text("Easy", center=easy_button_rect.center, fontsize=80, color=easy_color)
        
        # 绘制高难度按钮背景和文字
        hard_button_rect = Rect((WIDTH // 2 - 150, 500), (300, 100))
        hard_color = "white" if hard_button_rect.collidepoint(mouse_pos) else "brown"
        screen.draw.text("Hard", center=hard_button_rect.center, fontsize=80, color=hard_color)
    else:
        screen.blit('back', (0, 0))  # 背景图
        for tile in tiles:
            # 绘制上方牌组
            tile.draw()
            if tile.status == 0:
                screen.blit('mask', tile.topleft)  # 不可点的添加遮罩
        for i, tile in enumerate(docks):
            # 绘制排队，先调整一下位置
            tile.left = (DOCK.x + i * T_WIDTH)
            tile.top = DOCK.y
            tile.draw()

        # 超过7张，失败
        if len(docks) >= 7:
            screen.blit('end', (0, 0))
        # 没有剩牌，胜利
        if len(tiles) == 0:
            screen.blit('win', (0, 0))

        # 绘制倒计时
        draw_time()
        # 绘制分数
        draw_score()

# 鼠标点击响应
def on_mouse_down(pos):
    global game_started, easy_mode, score
    if not game_started:
        if 250 <= pos[0] <= 350 and 350 <= pos[1] <= 450:
            easy_mode = True
            game_started = True
            initialize_game()
        elif 250 <= pos[0] <= 350 and 500 <= pos[1] <= 600:
            easy_mode = False
            game_started = True
            initialize_game()
    else:
        global docks
        if len(docks) >= 7 or len(tiles) == 0:  # 游戏结束不响应
            return
        for tile in reversed(tiles):  # 逆序循环是为了先判断上方的牌，如果点击了就直接跳出，避免重复判定
            if tile.status == 1 and tile.collidepoint(pos):
                # 状态1可点，并且鼠标在范围内
                tile.status = 2
                tiles.remove(tile)
                diff = [t for t in docks if t.tag != tile.tag]  # 获取牌堆内不相同的牌
                if len(docks) - len(diff) < 2:  # 如果相同的牌数量<2，就加进牌堆
                    docks.append(tile)
                else:  # 否则用不相同的牌替换牌堆（即消除相同的牌）
                    docks = diff
                    score += 1  # 每消除三个方块计1分
                for down in tiles:  # 遍历所有的牌
                    if down.layer == tile.layer - 1 and down.colliderect(tile):  # 如果在此牌的下一层，并且有重叠
                        for up in tiles:  # 那就再反过来判断这种被覆盖的牌，是否还有其他牌覆盖它
                            if up.layer == down.layer + 1 and up.colliderect(down):  # 如果有就跳出
                                break
                        else:  # 如果全都没有，说明它变成了可点状态
                            down.status = 1
                return

music.play('bgm')
pgzrun.go()