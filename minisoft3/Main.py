from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import os
from functools import partial

PATH_PROJECT = './minisoft3/'
PATH_IMAGES = PATH_PROJECT+'images/'
PATH_IMAGES_PLAYER = PATH_IMAGES + 'player/'
TRANSLATOR = {'heal':'život +1', 
              'damage':'život -1', 
              'move_right':'doprava', 
              'move_left':'doľava', 
              'move_up':'hore', 
              'move_down':'dole'}

class Cell:
    def __init__(self, emoji, operations):
        self.emoji = emoji
        self.operations = operations
        self.is_changeable = operations == []

    def execute_move(self):
        self.emoji.attributes['stamina'] -= 1
        for op in self.operations:
            operation = Main.OPERATIONS[op]
            temp = set()
            for att in operation['attributes']:
                temp.add(att[0])
            if temp & set(['life','is_in_goal']) == set():
                for att in operation['attributes']:
                    if att[0] == 'life':
                        self.emoji.damage_or_heal(att[1])
                    else:
                        self.emoji.attributes[att[0]] += att[1]

    def execute_effects(self):
        for op in self.operations:
            operation = Main.OPERATIONS[op]
            temp = set()
            for att in operation['attributes']:
                temp.add(att[0])
            if temp & set(['life','is_in_goal']) != set():
                for att in operation['attributes']:
                    if att[0] == 'life':
                        self.emoji.damage_or_heal(att[1])
                    else:
                        self.emoji.attributes[att[0]] += att[1]
                


class Emoji:
    def __init__(self, life, stamina):
        self.attributes = dict()
        self.attributes['row'] = 0
        self.attributes['col'] = -1
        self.attributes['life'] = life
        self.attributes['stamina'] = stamina
        self.attributes['is_in_goal'] = 0
        self.images = [PhotoImage(file=PATH_IMAGES_PLAYER+'life_0.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_1.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_2.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_3.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'init.png')]
        self.life_image = Main.OPERATIONS['heal']['image']

    def can_execute(self):
        return self.attributes['life'] > 0 and self.attributes['is_in_goal'] == 0 and self.attributes['stamina'] > 0

    def move(self, dRow=0, dCol=0):
        if self.attributes['stamina'] > 0:
            self.attributes['stamina'] -= 1
            self.attributes['row'] += dRow
            self.attributes['col'] += dCol

    def damage_or_heal(self, lifes):
        if self.attributes['life'] + lifes >= 0 and self.attributes['life'] + lifes <= len(self.images)-2:
            self.attributes['life'] += lifes
            return True
        return False

    def paint(self, canvas):
        image = self.images[self.attributes['life']]
        if self.attributes['col'] == -1:
            image = self.images[-1]
        canvas.create_image((self.attributes['col']+1.5)*Main.CELL_WIDTH,(self.attributes['row']+1.5)*Main.CELL_HEIGHT,image=image)
        for i in range(self.attributes['life']):
            canvas.create_image((i+0.5)*Main.CELL_WIDTH,0.5*Main.CELL_HEIGHT,image=self.life_image)

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
        b = Button(self.canvas_top, text='Spusti', command=self.start_move)
        b.place(x=90, y=10)
        b = Button(self.canvas_top, text='Znova', command=self.reset)
        b.place(x=138, y=10)
        b = Button(self.canvas_top, text='Vytvor mapu', command=self.create_map)
        b.place(x=188, y=10)
        b = Button(self.canvas_top, text='Ulož mapu', command=self.select_file_save)
        b.place(x=272, y=10)
        # BINDINGS
        self.canvas_bottom.bind('<Button-1>', self.choosing_menu)

        self.load_operations()

        # MENU
        self.menu = Menu(self.canvas_bottom, tearoff=0)
        for operation in self.OPERATIONS:
            if operation not in ['goal', 'empty']:
                self.menu.add_command(label=TRANSLATOR[operation], command=partial(self.add_operation, operation))
        
        self.map = []
        self.emoji = None
        self.selected_cell = None
        self.filename = None
        self.was_reset = False
        self.paint()

    def choosing_menu(self,event):
        self.selected_cell = None
        col = (event.x - self.CELL_WIDTH) // self.CELL_WIDTH
        row = (event.y - self.CELL_HEIGHT) // self.CELL_HEIGHT
        if 0 <= row < len(self.map) and 0 <= col < len(self.map[row]) and self.map[row][col].is_changeable:
            self.selected_cell = self.map[row][col]
        if self.selected_cell is None:
            return
        try:
            self.menu.tk_popup(event.x_root+55, event.y_root, 0)
        finally:
            self.menu.grab_release()

    def add_operation(self, operation):
        if self.selected_cell is not None:
            if operation in self.selected_cell.operations:
                self.selected_cell.operations.remove(operation)
            else:
                self.selected_cell.operations.append(operation)
            self.selected_cell = None
            self.paint()
    
    def reset(self):
        if self.emoji is not None:
            self.start_game(self.filename)
            self.was_reset = True

    def create_map(self):
        rows = simpledialog.askinteger(title="Riadky", prompt='Počet riadkov')
        cols = simpledialog.askinteger(title="Stĺpce", prompt='Počet stĺpcov')
        self.map = []
        self.emoji = None
        for i in range(rows):
            temp = []
            for j in range(cols):
                temp.append(Cell(self.emoji,[]))
            self.map.append(temp)
        self.paint()

    def save_map(self,filename):
        with open(filename, 'w') as file:
            for row in self.map:
                file.write('#'.join([' '.join(cell.operations) for cell in row])+'\n')


    def select_file_save(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".json")
        if filename is not None and filename.name:
            self.save_map(filename.name)


    def load_operations(self):
        self.OPERATIONS['empty'] = dict()
        self.OPERATIONS['empty']['attributes'] = []
        self.OPERATIONS['empty']['image'] = PhotoImage(file=PATH_IMAGES+'empty.png')
        if os.path.isfile(PATH_PROJECT+'./operations.txt'):
            with open(PATH_PROJECT+'./operations.txt', 'r') as file:
                for row in file:
                    operation = row.split('#')
                    name = operation[0]
                    attributes = operation[1].split()
                    values = operation[2].split()
                    if len(attributes) == len(values) and len(values) > 0:
                        self.OPERATIONS[name] = dict()
                        self.OPERATIONS[name]['attributes'] = []
                        self.OPERATIONS[name]['image'] = PhotoImage(file=PATH_IMAGES+name+'.png')
                        for i in range(len(attributes)):
                            self.OPERATIONS[name]['attributes'].append([attributes[i], int(values[i])])


    def start_game(self, filename):
        self.filename = filename
        self.map = []
        self.emoji = Emoji(3,10)
        with open(filename, 'r') as file:
            for row in file:
                line = row.split('#')
                temp = []
                for col in row.split('#'):
                    temp.append(Cell(self.emoji, col.split()))
                self.map.append(temp)
        self.paint()

    def are_all_cells_selected(self):
        for row in self.map:
            for col in row:
                if col.operations == []:
                    return False
        return True

    def start_move(self):
        if self.emoji is not None and self.emoji.attributes['col'] == -1 and self.are_all_cells_selected():
            self.emoji.attributes['row'] = 0
            self.emoji.attributes['col'] = 0
            self.map[0][0].execute_effects()
            self.paint()
            self.canvas_bottom.after(1000,self.animate)

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            self.infile = open(filename, "r")
            self.start_game(filename)

    def animate(self):
        if self.was_reset:
            self.was_reset = False
            return
        if self.emoji is not None and self.emoji.can_execute():
            self.map[self.emoji.attributes['row']][self.emoji.attributes['col']].execute_move()
            self.map[self.emoji.attributes['row']][self.emoji.attributes['col']].execute_effects()
            self.paint()
            self.canvas_bottom.update()
            self.canvas_bottom.after(1000,self.animate)
    
    def paint(self):
        self.canvas_bottom.delete('all')
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j].is_changeable:
                    self.canvas_bottom.create_rectangle((j+1)*self.CELL_WIDTH,(i+1)*self.CELL_HEIGHT,(j+2)*self.CELL_WIDTH,(i+2)*self.CELL_HEIGHT,fill='yellowgreen')
                else:
                    self.canvas_bottom.create_rectangle((j+1)*self.CELL_WIDTH,(i+1)*self.CELL_HEIGHT,(j+2)*self.CELL_WIDTH,(i+2)*self.CELL_HEIGHT,fill='dodgerblue')
                for operation in self.map[i][j].operations:
                    self.canvas_bottom.create_image((j+1.5)*self.CELL_WIDTH,(i+1.5)*self.CELL_HEIGHT,image=self.OPERATIONS[operation]['image'])
                if self.map[i][j].operations == []:
                    self.canvas_bottom.create_image((j+1.5)*self.CELL_WIDTH,(i+1.5)*self.CELL_HEIGHT,image=self.OPERATIONS['empty']['image'])
        if self.emoji is not None:
            self.emoji.paint(self.canvas_bottom)



if __name__ == "__main__":
    m = Main()
    m.window.mainloop()
