import pygame
import tkinter as tk
from tkinter import filedialog
from random import randint

root = tk.Tk()
root.withdraw()

pygame.init()
MaxKey = 0

font = pygame.font.Font(None, 30)

def dist(a, b = [0, 0]):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def is_in(a, b):
    for el in a:
        if el not in b:
            return False
    return True

def save_lab(FName):
    file = open(FName, 'w')
    print(len(islands), file = file)
    for isl in islands:
        print(*isl.pos, file = file)
        print(1 if isl.side else 0, file = file)
        print(len(isl.connections), file = file)
        for con in isl.connections:
            print(con.to, con.key, sep = '\n', file = file)
            print(*con.start, file = file)
            print(*con.finish, file = file)

def load_lab(FName):
    isls = []
    file = open(FName, 'r')
    for i in range(int(file.readline())):
        isls.append(island([int(x) for x in file.readline().split()], side = file.readline() == '1\n'))
        for j in range(int(file.readline())):
            isls[-1].connections.append(connection(int(file.readline()), int(file.readline()), [int(x) for x in file.readline().split()], [int(x) for x in file.readline().split()]))
    return isls

class button:
    rect = [0, 0, 0, 0]
    text = ''
    colors = []
    t_cols = []
    frame = 0
    state = 0
    def __init__(self, rect, text, cls, text_cols = 0, frame = 0):
        self.frame = frame
        cols = cls.copy()
        self.rect = rect.copy()
        self.text = text
        main_color = cols[0]
        self.colors = []
        self.colors.append(main_color)
        if len(cols) == 1:
            self.colors.append([2 * x // 3 for x in main_color])
            self.colors.append([x // 3 for x in main_color])
        if text_cols == 0:
            for col in self.colors:
                S = sum(col)
                if S > (255 * 3) / 2:
                    self.t_cols.append([0, 0, 0])
                else:
                    self.t_cols.append([255, 255, 255])
        else:
            self.t_cols = text_cols.copy()
    def get_state(self, bkey = 0):
        pos = pygame.mouse.get_pos()
        pr = pygame.mouse.get_pressed()[bkey]
        if (self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2]) and (self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]):
            if pr:
                self.state = 2
                return 2
            else:
                self.state = 1
                return 1
        else:
            self.state = 0
            return 0
    def draw_and_state(self, scr, prsd = False, mark_len = 0, bkey = 0):
        self.state = self.get_state(bkey)
        state = self.state
        if prsd:
            state = 2
        try:
            col = self.colors[state]
        except:
            print(self.colors, state)
        pygame.draw.rect(scr, [0, 0, 0], self.rect)
        pygame.draw.rect(scr, col, [self.rect[0] + self.frame, self.rect[1] + self.frame, self.rect[2] - 2 * self.frame, self.rect[3] - 2 * self.frame])
        if mark_len != 0:
            pygame.draw.line(scr, (255, 0, 0), [self.rect[0] + self.rect[2] + 2, self.rect[1] + self.rect[3] // 2], [self.rect[0] + self.rect[2] + 2 + mark_len, self.rect[1] + self.rect[3] // 2], 5)
        scr.blit(font.render(self.text, 0, self.t_cols[state]), [x + 1 for x in self.rect[:2]])
        return state



class connection:
    to = 0
    start = [0, 0]
    finish = [0, 0]
    key = 0
    v_start = [0, 0]
    v_finish = [0, 0]
    def __init__(self, to, key, start, finish):
        self.to = to
        self.key = key
        self.start = start.copy()
        self.finish = finish.copy()

def list_to_code(lst):
    szx = 4
    szy = 4
    scr = pygame.Surface([max([0] + [len(x) for x in lst]) * szx, len(lst) * (szy + 2)])
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            pygame.draw.rect(scr, pos_col[lst[i][j]], [j * szx, i * (szy + 2), 4, 4])
    scr.set_colorkey([0, 0, 0])
    return scr

def count_to(cons, con):
    S = 0
    X = 0
    for i in range(len(cons)):
        if cons[i].to == con.to:
            S += 1
        if cons[i] == con:
            X = S
    return [S, X]

def sign(x):
    if x == 0:
        return 0
    else:
        return x // abs(x)

def shift(start, finish, sh):
    if start[0] == finish[0]:
        K = 999999999
    else:
        K = (finish[1] - start[1]) / (finish[0] - start[0])
    if K != 0:
        K = -1 / K
    else:
        K = 999999999
    dX = int((sh * sh / (K * K + 1)) ** 0.5) * sign(sh)
    dY = int((sh * sh - dX * dX) ** 0.5) * sign(K) * sign(sh)
    return [[start[0] + dX, start[1] + dY], [finish[0] + dX, finish[1] + dY]]

def get_dist_to_connection(con, pos):
    start, finish = con.v_start, con.v_finish
    if start[0] == finish[0]:
        K = 999999999
    else:
        K = (finish[1] - start[1]) / (finish[0] - start[0])
    if K != 0:
        KK = -1 / K
    else:
        KK = 999999999
    B = pos[1] - pos[0] * KK
    b = finish[1] - finish[0] * K
    X = (b - B) / (KK - K)
    Y = K * X + b
    point = [X, Y]
    A = dist(point, start)
    B = dist(point, finish)
    C = dist(point, pos)
    D = dist(start, finish)
    if A + B >= D + 2:
        return min(dist(pos, start), dist(pos, finish))
    else:
        return C

class island:
    pos = [0, 0]
    connections = []
    key_sets = []
    color = [0, 0, 0]
    radius = 25
    def __init__(self, pos, cons = [], color = [255, 0, 0], side = False):
        self.pos = pos
        self.connections = cons.copy()
        self.color = color
        self.side = side
    def connect(self, isl, key, s, f):
        self.connections.append(connection(isl, key, s, f))
    def set_con_color(self, ind, col):
        self.connections[ind].key = col
    def check_set(self):
        KeySet = self.key_sets
        for i in range(len(KeySet))[::-1]:
            for j in range(len(KeySet)):
                if i != j and is_in(KeySet[j], KeySet[i]):
                    KeySet.pop(i)
                    break
    def draw_core(self, scr):
        if not self.side:
            pygame.draw.circle(scr, [100, 100, 100], self.pos, self.radius)
            pygame.draw.circle(scr, [50, 50, 50], self.pos, self.radius - 2)
        array = list_to_code(self.key_sets)
        scr.blit(array, [SZX - 90, SZY // 2] if self.side else [self.pos[0] - array.get_width() // 2, self.pos[1] - array.get_height() // 2])
    def draw(self, scr):
        start_pos = self.pos
        for con in self.connections:
            if self.side:
                start_pos = con.finish
            else:
                start_pos = self.pos
            if con.to != 0 and con.to != 1:
                N, index = count_to(self.connections, con)
                sft = index * (self.radius * 2) // (N + 1) - self.radius
                strt, fin = shift(start_pos, islands[con.to].pos, sft) if not self.side else [start_pos, islands[con.to].pos]
                pygame.draw.line(scr, pos_col[con.key], strt, fin, 2)
                con.v_start, con.v_finish = strt, fin
            else:
                pygame.draw.line(scr, pos_col[con.key], start_pos, con.finish, 2)
                con.v_start, con.v_finish = start_pos, con.finish
            islands[con.to].draw_core(scr)
        self.draw_core(scr)
        if False and not self.side:
            for i, line in enumerate(self.key_sets):
                scr.blit(font.render(str(line), 0, [0, 0, 0]), [self.pos[0], self.pos[1] + i * 24])
def connect(isl, ISL, key, arr, start, finish):
    arr[ISL].connections.append(connection(isl, key, start, finish))
    arr[isl].connections.append(connection(ISL, key, start, finish))
def set_con_color(arr, isl, ISL, col):
    for i in range(len(arr[isl].connections)):
        if arr[isl].connections[i][0] == ISL:
            arr[isl].connections[i][1] = col
    for i in range(len(arr[ISL].connections)):
        if arr[ISL].connections[i][0] == isl:
            arr[ISL].connections[i][1] = col
def get_keys(arr, ind = 0, preds = []):
    if ind == 1:
        return
    preds.append(arr[ind])
    cons = arr[ind].connections
    ks = arr[ind].key_sets
    for i in cons:
        con = [arr[i.to], i.key]
        #scr.fill([240, 240, 240])
        for IS in arr:
            IS.check_set()
            #IS.draw(scr)
        #pygame.display.update()
        if con[0] not in preds:
            #print('step')
            res = sorted([list(set(x + [con[1]])) for x in ks])
            arr[arr.index(con[0])].key_sets = sorted(con[0].key_sets + res)
            get_keys(arr, ind=arr.index(con[0]), preds=preds.copy())

def remove_connection(con):
    for IS in islands:
        if con in IS.connections:
            IS.connections.pop(IS.connections.index(con))

def remove_island(ind):
    islands.pop(ind)
    for IS in islands:
        for i, con in list(enumerate(IS.connections))[::-1]:
            if ind == con.to:
                IS.connections.pop(i)
            elif con.to > ind:
                con.to -= 1

KG = True

MIN = 0
key = 0
SZX = 1100
SZY = 700
scr = pygame.display.set_mode([SZX, SZY])

islands = ([island([-1000000, SZY // 2], color = [0, 255, 0], side = True), island([1000000, SZY // 2], color = [0, 255, 0], side = True)])[::-1]
islands[0].key_sets = [[]]

pos_col = [[0, 0, 255],
           [0, 255, 0],
           [255, 0, 0],
           [127, 127, 0],
           [127, 0, 127],
           [0, 127, 127],
           [100, 0, 0],
           [0, 100, 0],
           [0, 0, 100]]

save = button([0, 0, 101, 20], 'export', [[0, 100, 255]])
load = button([0, 20, 101, 20], 'import', [[250, 0, 0]])
erase = button([0, SZY - 70, 101, 20], 'erase', [[255, 0, 0]])
create = button([0, SZY - 90, 101, 20], 'create', [[0, 255, 0]])

col_buttons = []
step = 25#(SZY - 70) // len(pos_col)
for i in range(len(pos_col)):
    col_buttons.append(button([0, 40 + i * step, 25, step], '', [pos_col[i]], frame = 2))

background = pygame.Surface([SZX, SZY])
background.fill([50, 50, 50])
for i in range(0, SZX, 50):
    pygame.draw.line(background, [100, 100, 100], [i, 0], [i, SZY])
for i in range(0, SZY, 50):
    pygame.draw.line(background, [100, 100, 100], [0, i], [SZX, i])
pygame.draw.rect(background, [125, 125, 125], [0, 0, 100, SZY])
pygame.draw.rect(background, [125, 125, 125], [SZX - 100, 0, 100, SZY])
pygame.draw.rect(background, [75, 75, 75], [0, SZY - 50, SZX, 50])
background.blit(font.render('Modes:', 0, [255, 255, 255]), [0, SZY - 110])

conn_color = [0, 0, 255]

mem_m_pos = [0, 0]

mode = 0

able_to_save = True
able_to_load = True

change = False

while KG:
    scr.blit(background, [0, 0])
    MPos = list(pygame.mouse.get_pos())
    scrshot = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            KG = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (125 <= MPos[0] <= SZX - 125) and (0 <= MPos[1] <= SZY - 75):
                if mode == 0:
                    if event.button == 3:
                        islands.append(island(MPos))
                    if event.button == 1:
                        if len(islands) > 2:
                            mem_m_pos = MPos.copy()
                            if len(islands) > 0:
                                for IS in islands:
                                    if MIN == 0 or dist(MPos, MIN.pos) > dist(MPos, IS.pos):
                                        MIN = IS
                else:
                    if event.button == 3:
                        min_isl = 0
                        record = 10 ** 9
                        for i, IS in enumerate(islands):
                            dst = dist(IS.pos, MPos)
                            if dst < record:
                                record = dst
                                min_isl = i
                        if min_isl >= 2:
                            remove_island(min_isl)
                    if event.button == 1:
                        for i in range(2):
                            min_con = 0
                            record = 10 ** 9
                            for IS in islands:
                                for con in IS.connections:
                                    dst = get_dist_to_connection(con, MPos)
                                    if dst < record:
                                        min_con = con
                                        record = dst
                            remove_connection(min_con)
                    change = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if len(islands) > 0 and MIN != 0:
                    MPos = list(pygame.mouse.get_pos())
                    MN = island([-10 ** 9, -10 ** 9])
                    for IS in islands:
                        if (MN == 0 or dist(MPos, MN.pos) > dist(MPos, IS.pos)):
                            MN = IS
                    if (100 <= MPos[0] <= SZX - 100):
                        if MN != MIN:
                            connect(islands.index(MN), islands.index(MIN), key, islands, mem_m_pos, MPos)
                    else:
                        if MPos[0] < 100:
                            connect(0, islands.index(MIN), key, islands, mem_m_pos, MPos)
                        else:
                            connect(1, islands.index(MIN), key, islands, mem_m_pos, MPos)
                    MIN = 0
                    change = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                scrshot = True

    if change:
        for IS in islands:
            IS.key_sets = []
        islands[0].key_sets = [[]]
        get_keys(islands)
        for IS in islands:
            IS.check_set()
        change = False
    if MIN != 0:
        pygame.draw.line(scr, pos_col[key], pygame.mouse.get_pos(), MIN.pos, 1)
    min_con = 0
    record = 10 ** 9
    for IS in islands:
        for con in IS.connections:
            dst = get_dist_to_connection(con, MPos)
            if dst < record:
                min_con = con
                record = dst
    if min_con != 0 and mode == 1:
        pygame.draw.line(scr, [255, 255, 255, 100], min_con.v_start, min_con.v_finish, 4)
    min_isl = 0
    record = 10 ** 9
    for i, IS in enumerate(islands):
        dst = dist(IS.pos, MPos)
        if dst < record:
            record = dst
            min_isl = IS
    if min_isl != 0:
        pygame.draw.circle(scr, [255, 255, 255], min_isl.pos, min_isl.radius + 2)
    for IS in islands:
        IS.draw(scr)
    save_res = save.draw_and_state(scr)
    if save_res == 2 and able_to_save:
        FPath = filedialog.asksaveasfilename()
        if FPath != '':
            save_lab(FPath)
        able_to_save = False
    elif save_res != 2:
        able_to_save = True
    load_res = load.draw_and_state(scr)
    if load_res == 2 and able_to_load:
        file_path = filedialog.askopenfilename()
        if file_path != '':
            islands = load_lab(file_path)
        pygame.mouse.set_pos([200, 200])
        able_to_load = False
        change = True
    elif load_res != 2:
        able_to_load = True
    for i, but in enumerate(col_buttons):
        cond = i == key
        res = but.draw_and_state(scr, cond, 20 if cond else 0)
        if res == 2:
            key = i
    if erase.draw_and_state(scr, mode == 1) == 2:
        mode = 1
    if create.draw_and_state(scr, mode == 0) == 2:
        mode = 0
    if scrshot:
        name = filedialog.asksaveasfilename()
        f = open(name, 'w')
        f.close()
        if name != '':
            pygame.image.save(scr, name)
    pygame.display.update()
pygame.quit()
