import facebook
from PIL import Image, ImageColor, ImageDraw, ImageFont
import yaml

import constants as c
import GDriveManager as GDM

import random
import math
import copy
import io
import time
import json

class FBPage():
    def __init__(self, access_token):
        self.access_token = access_token
        self.graph = facebook.GraphAPI(access_token)
        self.msg = ''
        print('Connected to facebook page!')

    def post_image(self, img):
        img_obj = self.process_image(img)
        post_id = self.graph.put_photo(image = img_obj, message = self.msg)['post_id']
        print('Photo with post id: ' + post_id + ' has been successfully uploaded to facebook!')
        return post_id

    def process_image(self, img):
        b = io.BytesIO()
        img.save(b, "png")
        b.seek(0)
        return b

    def make_msg(self, game):
        self.msg = '{}\nScore: {}\nREACT to move the board:\n👍UP ❤️DOWN 😂LEFT 😮RIGHT 😡UNDO'.format(game.msg,
        int(game.score))

    def over_msg(self, game):
        self.msg = '{}\nScore: {}'.format(game.msg, int(game.score))

    def count_reactions(self,post_id):
        post = self.graph.get_object(id=post_id, fields='reactions')
        likes = 0
        loves = 0
        hahas = 0
        wows = 0
        angrys = 0
        try:
            for react in post['reactions']['data']:
                if 'gang' not in react['name'].lower():
                    if react['type'] == 'LIKE':
                        likes += 1
                    elif react['type'] == 'LOVE':
                        loves += 1
                    elif react['type'] == 'HAHA':
                        hahas += 1
                    elif react['type'] == 'WOW':
                        wows += 1
                    elif react['type'] == 'ANGRY':
                        angrys += 1
        except KeyError:
            pass
        return [likes,loves,hahas,wows,angrys]

class GamePainter():
    def __init__(self):
        self.img = Image.new("RGB", (410, 410), c.BACKGROUND_COLOR_GAME)
        self.canvas = ImageDraw.Draw(self.img, mode='RGB')
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                self.canvas.rectangle([(i*100+10, j*100+10), (i*100+100-1, j*100+100-1)],
                 fill=c.BACKGROUND_COLOR_CELL_EMPTY)

    def print_img(self):
        self.img.show()

    def update_img(self, board):
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    self.canvas.rectangle([(j*100+10, i*100+10), (j*100+100-1, i*100+100-1)], fill=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.canvas.rectangle([(j*100+10, i*100+10), (j*100+100-1, i*100+100-1)], fill=c.BACKGROUND_COLOR_DICT[board[i][j]])

                    font_size = 30
                    fill = c.CELL_COLOR_DICT[board[i][j]]

                    if board[i][j] in [2,4,8]:
                        pos = (j*100+46, i*100+32)

                    elif board[i][j] in [16,32,64]:
                        pos = (j*100+36, i*100+32)

                    elif board[i][j] in [128,256,512]:
                        pos = (j*100+27, i*100+32)

                    elif board[i][j] in [2048,4096,8192]:
                        pos = (j*100+18, i*100+32)

                    elif board[i][j] in [1024]:
                        pos = (j*100+16, i*100+32)
                    
                    elif board[i][j] in [32768,65536]:
                        font_size = 27
                        pos = (j*100+15 , i*100+34)
                    else:
                        font_size = 27
                        # x: +ve = left
                        # y: +ve = down
                        pos = (j*100+13 , i*100+34)

                    font = ImageFont.truetype("ClearSans-Bold.ttf", font_size, encoding="unic")
                    self.canvas.text(pos, f'{board[i][j]}', fill=fill, font=font)

class Game():
    def __init__(self):
        self.board = [[0]*4 for _ in range(4)]
        self.score = 0
        self.random_fours = 0
        self.msg = 'New Game!'
        self.prev_game = copy.deepcopy(self)
        
    def print_board(self):
        print('----------------')
        print(self.msg)
        print(f'Score: {self.score}')
        print(f'Random 4s: {self.random_fours}')
        for row in self.board:
            print(row)

    #### GAME INIT METHODS ####
    def new_game(self):
        self.__init__()
        self.random_init()
        self.random_init()
        self.prev_game = copy.deepcopy(self)

    def random_init(self):
        seed = [2, 2, 2, 4]
        x, y = self.random_point(len(self.board)-1)
        v = random.randint(0, len(seed)-1)
        self.board[x][y] = seed[v]
        if seed[v] == 4:
            self.random_fours += 1
        #return seed[v]
    
    def save_game(self, filename):
        game_copy = copy.deepcopy(self.__dict__)
        game_copy['prev_game'] = ''
        with open(filename, "w") as write_file:
            json.dump(game_copy, write_file)
        print('Game Saved')

    def load_game(self, filename):
        with open(filename, "r") as read_file:
            data = json.load(read_file)

        data['prev_game'] = data
        self.__dict__.update(data)        
            

    #### WIN CONDITION METHODS ####
    def game_over(self, win_tile=65536):
        if any(win_tile in row for row in self.board):
            self.msg = "You win!"
            return True

        # no empty tiles = potential loss
        elif not any(0 in row for row in self.board): 
            old_game = copy.deepcopy(self.__dict__)

            # try move the board in all four directions
            for key in range(4):
                self.move(key)
                # a move was possible so not a loss
                if self.msg != 'Board was unchanged':
                    self.__dict__.update(old_game) # restore old board
                    return False

                # restore board to try new move
                self.__dict__.update(old_game)

            # no moves were possible:
            self.msg = 'You lost...'
            return True
        
        return False

    def count_score(self):   
        score = 0
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i][j] > 2:
                    score += self.board[i][j]*(math.log(self.board[i][j])/math.log(2)-1)
        self.score = int(score - 4*self.random_fours)

    #### NEW TILE METHODS ####
    def random_point(self, size):
        x = random.randint(0, size)
        y = random.randint(0, size)
        return (x, y)

    def random_tile(self):
        seed = [2, 2, 2, 4]
        x, y = self.random_point(len(self.board)-1)
        if self.board[x][y] == 0:
            v = random.randint(0, len(seed)-1)
            self.board[x][y] = seed[v]
            if seed[v] == 4:
                self.random_fours += 1
            #return seed[v]
        else: 
            return self.random_tile()

    #### BOARD MOVEMENT METHODS ####
    def stack(self):
        """
            Shift the game board's tiles to the left
        """
        new_board = [[0]*4 for _ in range(4)]
        for i in range(4):
            fill_position = 0
            for j in range(4):
                if self.board[i][j] != 0:
                    new_board[i][fill_position] = self.board[i][j]
                    fill_position += 1
        self.board = new_board   

    def combine(self):
        """
            Combines the game board's tiles to the left
        """
        for i in range(4):
            for j in range(3):
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i][j + 1]:
                    self.board[i][j] *= 2
                    self.board[i][j + 1] = 0

    def reverse(self):
        new_board = []
        for i in range(4):
            new_board.append([])
            for j in range(4):
                new_board[i].append(self.board[i][3 - j])
        self.board = new_board

    def transpose(self):
        new_board = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                new_board[i][j] = self.board[j][i]
        self.board = new_board
    
    def move_left(self):
        self.stack()
        self.combine()
        self.stack()
    
    def move(self, key):
        old_game = copy.deepcopy(self)
        if key == 0 or key == "w":
            #old_game = copy.deepcopy(self)
            self.msg = 'Board moved up!'
            self.transpose()
            self.move_left()
            self.transpose()

        elif key == 1 or key == "s":
            #old_game = copy.deepcopy(self)
            self.msg = 'Board moved down!'
            self.transpose()
            self.reverse()
            self.move_left()
            self.reverse()
            self.transpose()

        elif key == 2 or key == "a": 
            #old_game = copy.deepcopy(self)
            self.msg = 'Board moved left!'
            self.move_left()

        elif key == 3 or key == "d": 
            #old_game = copy.deepcopy(self)
            self.msg = 'Board moved right!'
            self.reverse()
            self.move_left()
            self.reverse()

        elif key == 4 or key == "z":
            if self.board == self.prev_game.board:
                self.msg = 'Board was unchanged'
                return
            self.__dict__.update(self.prev_game.__dict__)
            self.msg = 'Move undone!'
            return

        else:
            self.msg = 'Board was unchanged'
            return

        if self.board == old_game.board:
            self.msg = 'Board was unchanged'
            return
        else:
            self.prev_game = copy.deepcopy(old_game)
            if any(0 in row for row in self.board):
                self.random_tile()

def main():
    FILENAME = "saved_game.json"
    drive, _, save_file = GDM.init_drive()
    POSTING = True

    if POSTING:
        c.switch_cell_palette()
        with open('settings.yaml') as settings:
            access_token = yaml.full_load(settings)['fb_access_token']
        fb = FBPage(access_token)
        gp = GamePainter()
    
    game = Game()
    while True:
        try:
            GDM.load_file(drive, save_file)
            game.load_game(FILENAME)
            game.msg = 'Game was reloaded'
            print("Save file was found! Loading game...")
        except (FileNotFoundError,json.JSONDecodeError):
            print("Save game not found, creating new game")
            game.new_game()
        
        game.count_score()
        game.prev_game = copy.deepcopy(game)
        
        game.print_board()
        if POSTING:
            gp.update_img(game.board)
            fb.make_msg(game)
            post_id = fb.post_image(gp.img)
        
        game.save_game(FILENAME)
        GDM.update_file(drive,save_file,"saved_game.json")
        
        PLAYING = True
        while PLAYING:
            if POSTING:
                print('Awaiting reactions...')
                time.sleep(3600)
                reacts = fb.count_reactions(post_id)
                if reacts == [0]*5 or reacts.count(max(reacts)) > 1:
                    key = ''
                else:
                    key = reacts.index(max(reacts))
            else:
                key = input("Enter move: ")

            game.move(key)
            game.count_score()
            
            if game.game_over():
                PLAYING = False

            game.print_board()
            game.save_game(FILENAME)
            GDM.update_file(drive,save_file,"saved_game.json")
            if POSTING:
                if key == '':
                    c.switch_cell_palette()
                gp.update_img(game.board)
                if PLAYING:
                    fb.make_msg(game)
                else:
                    fb.over_msg(game)
                post_id = fb.post_image(gp.img)

if __name__ == '__main__':
    main()