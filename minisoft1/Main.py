from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import glob
import sys
from PIL import Image
from PIL import ImageTk
import os
from functools import partial
import random

PATH_IMAGES = './images/'
PATH_RULES = PATH_IMAGES + 'rules/'
PATH_PROCESSED = PATH_IMAGES + 'processed/'


class Node:
    def __init__(self, data, next_node=None):
        self.data = data
        self.next_node = next_node

    def equals(self, node):
        pom = self
        while True:
            if pom is None and node is None:
                return True
            if pom is None or node is None:
                return False
            if pom.data.char_name != node.data.char_name:
                return False
            pom = pom.next_node
            node = node.next_node



class Character:
    HEIGHT = 40
    WIDTH = 130
    ARROW = 32

    def __init__(self, file_name, name):
        self.char_name = name
        self.file_name = file_name
        image = Image.open(file_name)
        image = image.resize((self.WIDTH, self.HEIGHT), Image.ANTIALIAS)
        image.save(PATH_PROCESSED + self.char_name + '.png', 'PNG')
        self.image = ImageTk.PhotoImage(Image.open(PATH_PROCESSED + self.char_name + '.png'))

class Rule:
    RULE_WIDTH = Character.WIDTH * 2 + Character.ARROW
    def __init__(self, line):
        self.name = line.strip()
        array = self.name.split(' -> ')
        if len(array) != 2:
            raise ValueError
        self.search = array[0].split(',')
        self.replace = array[1].split(',')
        self.replace_characters = []
        self.search_characters = []
        self.height = max(len(self.search), len(self.replace))*Character.HEIGHT
        self.image = None

    def set_characters(self, characters, alphabet):
        for i in self.search:
            self.search_characters.append(characters[i])
            alphabet.add(characters[i])
        for i in self.replace:
            self.replace_characters.append(characters[i])
            alphabet.add(characters[i])
        self.combine_images()

    def combine_images(self):
        image1 = map(Image.open, [PATH_PROCESSED + i.char_name + '.png' for i in self.search_characters])
        image2 = map(Image.open, [PATH_PROCESSED + i.char_name + '.png' for i in self.replace_characters])
        new_image = Image.new('RGBA', (Character.WIDTH * 2 + Character.ARROW, self.height), 'white')

        y_offset = (self.height - len(self.search_characters) * Character.HEIGHT) // 2
        for im in image1:
            new_image.paste(im, (0, y_offset))
            y_offset += Character.HEIGHT

        new_image.paste(Image.open(PATH_IMAGES + '/arrow.png'), (Character.WIDTH, (self.height - Character.ARROW) // 2))

        y_offset = (self.height - len(self.replace_characters) * Character.HEIGHT) // 2
        for im in image2:
            new_image.paste(im, (Character.WIDTH+Character.ARROW, y_offset))
            y_offset += Character.HEIGHT
        file_name = self.name.replace(',', '_').replace(' -> ', 'A')

        new_image.save(PATH_RULES + file_name + '.png', "PNG")

        self.image = ImageTk.PhotoImage(Image.open(PATH_RULES + file_name + '.png'))


class Main:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    TOP_WIDTH = WINDOW_WIDTH
    TOP_HEIGHT = 50
    LEFT_WIDTH = Rule.RULE_WIDTH+20
    LEFT_HEIGHT = WINDOW_HEIGHT - TOP_HEIGHT
    RIGHT_WIDTH = TOP_WIDTH - LEFT_WIDTH-25
    RIGHT_HEIGHT = LEFT_HEIGHT

    def __init__(self):
        self.window = Tk()
        self.window.title('Burgraren')
        frame = Frame(self.window).pack()
        # TOP
        self.canvas_top = Canvas(frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # LEFT
        self.canvas_left = Canvas(frame, width=self.LEFT_WIDTH, height=self.LEFT_HEIGHT, bg='#bada55',
                                  scrollregion=(0,0,self.LEFT_WIDTH,self.LEFT_HEIGHT+50))
        vbar = Scrollbar(frame, orient=VERTICAL)
        vbar.pack(side=LEFT, fill=Y)
        vbar.config(command=self.canvas_left.yview)
        self.canvas_left.config(yscrollcommand=vbar.set)
        self.canvas_left.pack(side=LEFT, expand=True)
        # RIGHT
        self.canvas_right = Canvas(frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT, bg='lightgreen')
        self.canvas_right.pack(side=RIGHT, expand=False)
        b = Button(self.canvas_top, text='Vyber súbor', command=self.select_file)
        b.place(x=10,y=10)
        b = Button(self.canvas_top, text='Nastav Slovo', command=self.init_words)
        b.place(x=150,y=10)
        b = Button(self.canvas_top, text='Začni znova', command=self.reset)
        b.place(x=300, y=10)
        self.button_rules = []
        self.start = None
        self.goal = None
        self.start_game()

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        self.infile = open(filename, "r")
        self.start_game(filename)

    def start_game(self,file_name='config.txt'):
        self.steps = []
        self.alphabet = set()
        self.canvas_left.delete('all')
        self.canvas_right.delete('all')
        if self.button_rules != []:
            for but in self.button_rules:
                but.place_forget()
        self.characters = dict()
        self.rules = dict()

        os.makedirs(PATH_PROCESSED, exist_ok=True)
        os.makedirs(PATH_RULES, exist_ok=True)

        self.burger = [ImageTk.PhotoImage(Image.open(PATH_IMAGES + 'burger_top.png')),
                        ImageTk.PhotoImage(Image.open(PATH_IMAGES + 'burger_bottom.png'))]
        self.my_word = None
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                row = file.readline().strip()

                for i in glob.glob(row+'/*.png'):
                    absolute_path = i.replace('\\', '/')
                    file_name = absolute_path.split('/')[-1]
                    char = file_name.split('.')[0]
                    self.characters[char] = Character(absolute_path, char)

                row = file.readline().strip()
                while row != '':
                    try:
                        rule = Rule(row)
                        rule.set_characters(self.characters, self.alphabet)
                        self.rules[row] = rule
                    except:
                        print('Zly format pravdila: '+row)
                    row = file.readline().strip()
                print(self.rules)
        #self.init_words('a,b,c,d')
        print(self.alphabet)
        self.init_paint()

    def paint_rules(self):
        x = 10
        y = 10
        for key in self.rules:
            rule = self.rules[key]
            self.button_rules.append(
                Button(master=self.canvas_left, command=partial(self.apply_rule, rule.name), image=rule.image,
                       state=ACTIVE))
            self.button_rules[-1].place(x=x, y=y)
            y += rule.height + 10
        return y

    def paint_start_word(self,x,y):
        self.canvas_left.create_image(x, y, image=self.burger[0], anchor=NW)
        y += Character.HEIGHT
        pom = self.start
        while pom is not None:
            self.canvas_left.create_image(x, y, image=pom.data.image, anchor=NW)
            y += Character.HEIGHT
            pom = pom.next_node
        print(y)
        self.canvas_left.create_image(x, y, image=self.burger[1], anchor=NW)

    def paint_goal_word(self,x,y):
        pom = self.goal
        self.canvas_left.create_image(x, y, image=self.burger[0], anchor=NW)
        y += Character.HEIGHT
        while pom is not None:
            self.canvas_left.create_image(x, y, image=pom.data.image, anchor=NW)
            y += Character.HEIGHT
            pom = pom.next_node
        self.canvas_left.create_image(x, y, image=self.burger[1], anchor=NW)

    def paint_alphabet(self):
        self.canvas_top.delete('all')
        x = self.TOP_WIDTH - Character.WIDTH - 5

        for character in self.alphabet:
            self.canvas_top.create_image(x, 5, image=character.image, anchor=NW)
            x -= Character.WIDTH - 5

    def init_paint(self):
        self.canvas_left.delete('all')
        y = self.paint_rules()
        initY = y
        x = 10

        self.paint_start_word(x,y)

        y = initY
        x += Character.WIDTH

        self.paint_goal_word(x,y)



    def init_words(self, word1=None):
        if word1 is None:
            word1 = ''
            for i in range(random.randrange(3,6)):
                char = random.choice(list(self.alphabet))
                if i == 0:
                    word1 += char.char_name
                else:
                    word1 += ','+char.char_name
        self.canvas_right.delete('all')
        for but in self.button_rules:
            but.config(state=ACTIVE)
        characters = word1.split(',')
        self.start = Node(self.characters[characters[0]])
        pom = self.start
        self.my_word = Node(self.characters[characters[0]])
        pom2 = self.my_word
        self.goal = Node(self.characters[characters[0]])
        pom3 = self.goal

        for c in characters[1:]:
            pom.next_node = Node(self.characters[c])
            pom = pom.next_node
            pom2.next_node = Node(self.characters[c])
            pom2 = pom2.next_node
            pom3.next_node = Node(self.characters[c])
            pom3 = pom3.next_node
        self.generate_goal_word()
        self.init_paint()

    def apply(self,node,rule_key):
        while node is not None:
            rule = self.rules[rule_key]
            if node.data.char_name == rule.search_characters[0].char_name:
                temp = node
                first_node = node
                last_node = None
                is_equal = True
                for i in rule.search_characters:
                    is_equal = is_equal and (temp.data.char_name == i.char_name)
                    temp = temp.next_node
                    last_node = temp
                if is_equal:
                    node.data = self.characters[rule.replace_characters[0].char_name]
                    for i in rule.replace_characters[1:]:
                        node.next_node = Node(self.characters[i.char_name])
                        node = node.next_node
                    node.next_node = last_node
                    print(rule.name)
                    return True
            node = node.next_node
        return False

    def generate_goal_word(self):
        p = list(self.rules.keys())
        for i in range(random.randrange(2,4)):
            pom = self.goal
            random.shuffle(p)
            for r in p:
                if self.apply(pom,r):
                    break

    def reset(self):
        pom = self.start
        first_node = Node(pom.data)
        temp = first_node
        while pom.next_node is not None:
            pom = pom.next_node
            temp.next_node = Node(pom.data)
            temp = temp.next_node
        self.my_word = first_node
        self.print_next_step()


    def apply_rule(self, key, is_init=False):
        pom = self.my_word
        is_applied = self.apply(pom, key)
        self.steps.append(key)
        pom = self.my_word
        while pom is not None:
            print(pom.data.char_name,end=' ')
            pom = pom.next_node
        print()
        if not is_init:
            self.print_next_step()
            self.check_if_end()

    def check_if_end(self):
        if self.my_word.equals(self.goal):
            for but in self.button_rules:
                but.config(state=DISABLED)
            messagebox.showinfo("Výsledok", "Našli ste správny burger")

    def print_next_step(self):
        x = 10
        y = 10
        pom = self.my_word
        self.canvas_right.delete('all')
        self.canvas_right.create_image(x, y, image=self.burger[0], anchor=NW)
        y += Character.HEIGHT
        while pom is not None:
            self.canvas_right.create_image(x, y, image=pom.data.image, anchor=NW)
            y += Character.HEIGHT
            pom = pom.next_node
        self.canvas_right.create_image(x, y, image=self.burger[1], anchor=NW)



if __name__ == '__main__':
    main = Main()
    main.window.mainloop()
