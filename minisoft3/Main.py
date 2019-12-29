from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os

class Cell:
    def __init__(self, emoji, operations):
        self.emoji = emoji
        self.operations = operations

    def execute(self):
        for op in self.operations:
            operation = Main.OPERATIONS[op]
            for att in operation['attributes']:
                if att[0] == 'life':
                    self.emoji.damage_or_heal(att[1])


class Emoji:
    def __init__(self, life, stamina):
        self.attributes = dict()
        self.attributes['row'] = 0
        self.attributes['col'] = 0
        self.attributes['life'] = life
        self.attributes['stamina'] = stamina

    def move(self, dRow=0, dCol=0):
        if self.attributes['stamina'] > 0:
            self.attributes['stamina'] -= 1
            self.attributes['row'] += dRow
            self.attributes['col'] += dCol

    def damage_or_heal(self, lifes=-1):
        if self.attributes['life'] + lifes >= 0:
            self.attributes['life'] += lifes
            return True
        return False

class Main:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    TOP_WIDTH = WINDOW_WIDTH
    TOP_HEIGHT = 50
    BOTTOM_WIDTH = WINDOW_WIDTH
    BOTTOM_HEIGHT = WINDOW_HEIGHT - TOP_HEIGHT
    CELL_WIDTH = 64
    CELL_HEIGHT = 64
    OPERATIONS = dict()

    def __init__(self):
        self.window = Tk()
        self.window.title('Cestovatel')
        self.window.resizable(False, False)
        self.frame = Frame(self.window,bg='black').pack()
        # TOP
        self.canvas_top = Canvas(self.frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # BOTTOM
        self.canvas_bottom = Canvas(self.frame, width=self.BOTTOM_WIDTH, height=self.BOTTOM_HEIGHT, bg='tan')
        self.canvas_bottom.pack(side=BOTTOM, expand=False)
        # BUTTONS
        b = Button(self.canvas_top, text='Vyber mapu', command=self.select_file)
        b.place(x=10, y=10)

        self.load_operations()
        print(self.OPERATIONS)
        self.map = []
        self.emoji = Emoji
        self.paint()

    def load_operations(self):
        self.OPERATIONS['empty'] = dict()
        self.OPERATIONS['empty']['attributes'] = []
        self.OPERATIONS['empty']['image'] = PhotoImage(file='./minisoft3/images/empty.png')
        if os.path.isfile('./minisoft3/operations.txt'):
            with open('./minisoft3/operations.txt', 'r') as file:
                for row in file:
                    operation = row.split('#')
                    name = operation[0]
                    attributes = operation[1].split()
                    values = operation[2].split()
                    if len(attributes) == len(values) and len(values) > 0:
                        self.OPERATIONS[name] = dict()
                        self.OPERATIONS[name]['attributes'] = []
                        self.OPERATIONS[name]['image'] = PhotoImage(file='./minisoft3/images/'+name+'.png')
                        for i in range(len(attributes)):
                            self.OPERATIONS[name]['attributes'].append([attributes[i], int(values[i])])


    def start_game(self, filename):
        with open(filename, 'r') as file:
            for row in file:
                line = row.split('#')
                temp = []
                for col in row.split('#'):
                    if col == '?':
                        temp.append(Cell(self.emoji, ['empty']))
                    temp.append(Cell(self.emoji, col.split()))
                self.map.append(temp)
        self.paint()

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            self.infile = open(filename, "r")
            self.start_game(filename)
    
    def paint(self):
        self.canvas_bottom.delete('all')
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                for operation in self.map[i][j].operations:
                    self.canvas_bottom.create_image((j+1.5)*self.CELL_WIDTH,(i+1.5)*self.CELL_HEIGHT,image=self.OPERATIONS[operation]['image'])




if __name__ == "__main__":
    m = Main()
    m.window.mainloop()