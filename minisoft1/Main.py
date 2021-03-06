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
import re

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

    def size(self):
        count = 0
        pom = self
        while pom is not None:
            count += 1
            pom = pom.next_node
        return count

    def copy(self):
        new_root = Node(self.data)

        new_temp = new_root

        temp = self
        while temp.next_node is not None:
            temp = temp.next_node
            new_temp.next_node = Node(temp.data)
            new_temp = new_temp.next_node
        return new_root


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
        self.name = line
        if not re.match(r"[^/\\?%*:|\"<>]+ -> [^/\\?%*:|\"<>]+", self.name):
            raise ValueError
        array = self.name.strip().split(' -> ')
        self.search = array[0].split(',')
        self.replace = array[1].split(',')
        if len(self.search) > 3 or len(self.replace) > 3:
            raise AttributeError
        self.replace_characters = []
        self.search_characters = []
        self.height = max(len(self.search), len(self.replace)) * Character.HEIGHT
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
        new_image = Image.new('RGBA', (Character.WIDTH * 2 + Character.ARROW, self.height), (0, 0, 0, 0))

        y_offset = (self.height - len(self.search_characters) * Character.HEIGHT) // 2
        for im in image1:
            new_image.paste(im, (0, y_offset))
            y_offset += Character.HEIGHT

        new_image.paste(Image.open(PATH_IMAGES + '/arrow.png'), (Character.WIDTH, (self.height - Character.ARROW) // 2))

        y_offset = (self.height - len(self.replace_characters) * Character.HEIGHT) // 2
        for im in image2:
            new_image.paste(im, (Character.WIDTH + Character.ARROW, y_offset))
            y_offset += Character.HEIGHT
        file_name = self.name.replace(',', '_').replace(' -> ', 'A')

        new_image.save(PATH_RULES + file_name + '.png', "PNG")

        image = new_image.resize((int((Character.WIDTH * 2 + Character.ARROW) * 0.4), int(self.height * 0.4)), Image.ANTIALIAS)

        image.save(PATH_RULES + file_name + '_small.png', 'PNG')

        self.image = ImageTk.PhotoImage(Image.open(PATH_RULES + file_name + '.png'))
        self.image_for_step = ImageTk.PhotoImage(Image.open(PATH_RULES + file_name + '_small.png'))


class Main:
    WINDOW_WIDTH = 1220
    WINDOW_HEIGHT = 750
    TOP_WIDTH = WINDOW_WIDTH
    TOP_HEIGHT = 50
    LEFT_WIDTH = WINDOW_WIDTH
    LEFT_HEIGHT = Character.HEIGHT*4-18
    RIGHT_WIDTH = WINDOW_WIDTH
    RIGHT_HEIGHT = WINDOW_HEIGHT-LEFT_HEIGHT-TOP_HEIGHT

    def __init__(self):
        self.window = Tk()
        self.window.title('Burgraren')
        self.window.resizable(False, False)
        self.frame = Frame(self.window,bg='black').pack()
        # TOP
        self.canvas_top = Canvas(self.frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # LEFT
        self.canvas_rules = Canvas(self.frame, width=self.LEFT_WIDTH, height=self.LEFT_HEIGHT, bg='#bada55',
                                   scrollregion=(0, 0, self.LEFT_WIDTH, self.LEFT_HEIGHT))
        self.canvas_rules.pack(side=TOP, expand=False)

        # RIGHT
        self.background = ImageTk.PhotoImage(Image.open(PATH_IMAGES+'board.png'))
        self.canvas_right = Canvas(self.frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT)
        self.canvas_right.pack(side=TOP, expand=False)
        b = Button(self.canvas_top, text='Vyber súbor', command=self.select_file)
        b.place(x=10, y=10)
        b = Button(self.canvas_top, text='Nastav Slovo', command=self.generate_start_word)
        b.place(x=100, y=10)
        b = Button(self.canvas_top, text='Začni znova', command=self.reset)
        b.place(x=200, y=10)

        self.show_steps = BooleanVar()
        self.checkButton = Checkbutton(self.canvas_top, text="Zobrazit postup", variable=self.show_steps, height=1, width=11,
                                       command=self.print_next_step)
        self.checkButton.place(x=300, y=10)
        self.button_rules = []

        self.characters = dict()
        self.rules = dict()
        self.steps = []
        self.burger = []
        self.my_word = None

        self.start_game()

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            self.infile = open(filename, "r")
            self.start_game(filename)

    def start_game(self, file_name='config.txt'):
        self.canvas_rules.delete('all')
        self.canvas_right.delete('all')
        if self.button_rules:
            for but in self.button_rules:
                but.place_forget()
        self.characters = dict()
        self.rules = dict()
        self.alphabet = set()
        self.start = None
        self.goal = None
        self.steps = []

        os.makedirs(PATH_PROCESSED, exist_ok=True)
        os.makedirs(PATH_RULES, exist_ok=True)

        self.burger = [ImageTk.PhotoImage(Image.open(PATH_IMAGES + 'burger_top.png')),
                       ImageTk.PhotoImage(Image.open(PATH_IMAGES + 'burger_bottom.png'))]

        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                row = file.readline().strip()

                for i in glob.glob(row + '/*.png'):
                    absolute_path = i.replace('\\', '/')
                    file_name = absolute_path.split('/')[-1]
                    char = file_name.split('.')[0]
                    self.characters[char] = Character(absolute_path, char)

                row = file.readline().strip()
                while row != '':
                    try:
                        rule = Rule(row)
                        if len(self.rules) == 4:
                            messagebox.showinfo("Upozornenie", "Vstupný súbor môže obsahovať maximálne 4 pravidlá.\n\nOstatné nebudú použité!")
                            break
                        rule.set_characters(self.characters, self.alphabet)
                        self.rules[row] = rule
                    except ValueError:
                        print('Zly format pravdila: ' + row)
                    except AttributeError:
                        print('Pravidlo má priveľa znakov: ' + row)
                    except:
                        pass
                    row = file.readline().strip()
        self.init_paint()

    def generate_start_word(self):
        self.temp = []
        self.remove_buttons = []

        def paint_burger():
            self.canvas.delete('all')
            x = 10
            y = 10
            self.canvas.create_image(x, y, image=self.burger[0], anchor=NW)
            y += Character.HEIGHT
            for i in range(len(self.remove_buttons)):
                if self.remove_buttons[i][1]:
                    self.canvas.create_image(x,y,image=self.characters[self.temp[i][0]].image, anchor=NW)
                    self.remove_buttons[i][0].place(x=x+Character.WIDTH,y=y+10)
                    y += Character.HEIGHT
            self.canvas.create_image(x, y, image=self.burger[1], anchor=NW)


        def add_image(name):
            count = 0
            for item in self.temp:
                if item[1]:
                    count += 1
            if count > 3:
                return
            self.temp.append([name,True])
            self.remove_buttons.append([Button(master=self.canvas, command=partial(delete_image, len(self.temp)-1), text='x',
                   state=ACTIVE),True])
            paint_burger()

        def delete_image(index):
            self.remove_buttons[index][1] = False
            self.remove_buttons[index][0].destroy()
            self.temp[index][1] = False
            paint_burger()

        def start():
            res_word = []
            for character in self.temp:
                if character[1]:
                    res_word.append(character[0])
            self.init_words(','.join(res_word))
            self.temp = []
            self.remove_buttons = []
            self.window_create_word.destroy()

        self.window_create_word = Toplevel(self.frame)
        self.canvas = Canvas(self.window_create_word,width=400,height=(len(self.alphabet)+3)*Character.HEIGHT,bg='green')
        self.canvas.pack()

        y = 10
        for character in self.alphabet:
            b = Button(master=self.canvas, command=partial(add_image, character.char_name), image=character.image,
                   state=ACTIVE, height=Character.HEIGHT)
            b.place(x=400-Character.WIDTH-10,y=y)
            y += Character.HEIGHT + 10
        res_button = Button(master=self.canvas, command=start, text='Vytvor slovo',
                            state=ACTIVE)
        res_button.place(x=300-Character.WIDTH-10, y=y+10)
        paint_burger()


    def paint_rules(self):
        x = 10
        y = 10
        if self.button_rules:
            for but in self.button_rules:
                but.place_forget()
        self.button_rules = []
        for key in self.rules:
            rule = self.rules[key]
            self.button_rules.append(
                Button(master=self.canvas_rules, command=partial(self.apply_rule, rule.name), image=rule.image,
                       state=ACTIVE,height=Character.HEIGHT*3))
            self.button_rules[-1].place(x=x, y=y)
            x += Rule.RULE_WIDTH + 10
        return y

    def paint_start_word(self):
        self.canvas_right.create_image(0, 0, image=self.background, anchor=NW)
        x = 10
        y = 10
        self.canvas_right.create_image(x, y, image=self.burger[0], anchor=NW)
        y += Character.HEIGHT
        pom = self.start
        while pom is not None:
            self.canvas_right.create_image(x, y, image=pom.data.image, anchor=NW)
            y += Character.HEIGHT
            pom = pom.next_node
        self.canvas_right.create_image(x, y, image=self.burger[1], anchor=NW)

    def paint_goal_word(self):
        x = self.WINDOW_WIDTH-Character.WIDTH-10
        y = 10
        pom = self.goal
        self.canvas_right.create_image(x, y, image=self.burger[0], anchor=NW)
        y += Character.HEIGHT
        while pom is not None:
            self.canvas_right.create_image(x, y, image=pom.data.image, anchor=NW)
            y += Character.HEIGHT
            pom = pom.next_node
        self.canvas_right.create_image(x, y, image=self.burger[1], anchor=NW)

    def paint_alphabet(self):
        self.canvas_top.delete('all')
        x = self.TOP_WIDTH - Character.WIDTH - 5
        for character in self.alphabet:
            self.canvas_top.create_image(x, 5, image=character.image, anchor=NW)
            x -= Character.WIDTH - 5

    def init_paint(self):
        self.canvas_rules.delete('all')
        y = self.paint_rules()
        self.paint_alphabet()

        self.paint_start_word()

        self.paint_goal_word()



    def init_words(self, word1=None):
        self.steps = []
        if word1 is None or word1 == '':
            word1 = ''
            for i in range(random.randrange(3, 6)):
                char = random.choice(list(self.alphabet))
                if i == 0:
                    word1 += char.char_name
                else:
                    word1 += ',' + char.char_name
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
        self.print_next_step()

    def apply(self, node, rule_key):
        while node is not None:
            rule = self.rules[rule_key]
            if node.data.char_name == rule.search_characters[0].char_name:
                temp = node
                last_node = None
                is_equal = True
                for i in rule.search_characters:
                    is_equal = is_equal and temp is not None and (temp.data.char_name == i.char_name)
                    if temp is None:
                        break
                    temp = temp.next_node
                    last_node = temp
                if is_equal:
                    node.data = self.characters[rule.replace_characters[0].char_name]
                    for i in rule.replace_characters[1:]:
                        node.next_node = Node(self.characters[i.char_name])
                        node = node.next_node
                    node.next_node = last_node
                    return True
            node = node.next_node
        return False

    def generate_goal_word(self):
        p = list(self.rules.keys())
        for i in range(random.randrange(3, 5)):
            if self.goal.size() > 7:
                return
            pom = self.goal
            random.shuffle(p)
            for r in p:
                if self.apply(pom, r):
                    break

    def reset(self):
        self.steps = []
        pom = self.start
        first_node = Node(pom.data)
        temp = first_node
        while pom.next_node is not None:
            pom = pom.next_node
            temp.next_node = Node(pom.data)
            temp = temp.next_node
        for but in self.button_rules:
            but.config(state=ACTIVE)
        self.my_word = first_node
        self.print_next_step()

    def apply_rule(self, key, is_init=False):
        if self.my_word is None:
            return
        if len(self.steps) > 6:
            msg = messagebox.askquestion("Skúsiť znova", "Dané riešenie sa dá spraviť aj na menej krokov.\nChcete začať znova?")
            if msg == 'yes':
                self.reset()
            return
        pom = self.my_word
        is_applied = self.apply(pom, key)
        self.steps.append(key)
        pom = self.my_word
        if not is_init:
            self.print_next_step()
            self.check_if_end()

    def check_if_end(self):
        if self.my_word.equals(self.goal):
            for but in self.button_rules:
                but.config(state=DISABLED)
            messagebox.showinfo("Výsledok", "Našli ste správny burger")

    def print_next_step(self):
        x = Character.WIDTH+10
        y = 10
        self.canvas_right.delete('all')
        self.paint_start_word()
        self.paint_goal_word()
        if self.show_steps.get():
            start = self.start.copy()
            for i in range(len(self.steps)):
                self.apply(start, self.steps[i])
                pom = start
                self.canvas_right.create_image(x, y, image=self.burger[0], anchor=NW)
                y += Character.HEIGHT
                while pom is not None:
                    self.canvas_right.create_image(x, y, image=pom.data.image, anchor=NW)
                    y += Character.HEIGHT
                    pom = pom.next_node
                self.canvas_right.create_image(x, y, image=self.burger[1], anchor=NW)
                y += Character.HEIGHT + 10
                self.canvas_right.create_rectangle(x,y,x+self.rules[self.steps[i]].image_for_step.width()+4,
                                                   y+self.rules[self.steps[i]].image_for_step.height()+4,fill='white')
                self.canvas_right.create_image(x+2, y+2,
                                               image=self.rules[self.steps[i]].image_for_step, anchor=NW)
                x += Character.WIDTH+5
                y = 10

        else:
            if not self.steps:
                return
            pom = self.my_word
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
