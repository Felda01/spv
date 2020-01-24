from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import os
from functools import partial
import json
import re

PATH_PROJECT = './minisoft3/'
PATH_IMAGES = PATH_PROJECT+'images/'
PATH_IMAGES_PLAYER = PATH_IMAGES + 'player/'


class Cell:
    def __init__(self, emoji, operations):
        self.emoji = emoji
        self.operations = operations
        if self.operations == ['']:
            self.operations = []
        self.is_changeable = self.operations == []
        self.action_index = 0

    def next(self):
        if self.is_changeable:
            self.action_index = (self.action_index + 1) % len(Main.ADDED_ACTIONS)
            if self.action_index == 0:
                self.operations = []
            else:
                self.operations = [Main.ADDED_ACTIONS[self.action_index]]

    def execute_move(self):
        self.emoji.attributes['stamina'] -= 1
        for op in self.operations:
            operation = Main.OPERATIONS[op]
            temp = set()
            for att in operation['attributes']:
                temp.add(att[0])
            if temp & {'life', 'is_in_goal'} == set():
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
            if temp & {'life', 'is_in_goal'} != set():
                for att in operation['attributes']:
                    if att[0] == 'life':
                        self.emoji.damage_or_heal(att[1])
                    else:
                        self.emoji.attributes[att[0]] += att[1]


class Emoji:
    def __init__(self, life, stamina):
        self.is_death = False
        self.attributes = dict()
        self.attributes['row'] = 0
        self.attributes['col'] = -1
        self.attributes['life'] = life
        self.attributes['stamina'] = 1000
        self.attributes['is_in_goal'] = 0
        self.images = [PhotoImage(file=PATH_IMAGES_PLAYER+'life_0.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_1.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_2.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'life_3.png'),
                       PhotoImage(file=PATH_IMAGES_PLAYER+'init.png')]
        self.life_image = PhotoImage(file=PATH_IMAGES+'heal.png')

    def can_execute(self):
        return self.attributes['life'] > 0 and self.attributes['is_in_goal'] == 0 and self.attributes['stamina'] > 0

    def move(self, d_row=0, d_col=0):
        if self.attributes['stamina'] > 0:
            self.attributes['stamina'] -= 1
            self.attributes['row'] += d_row
            self.attributes['col'] += d_col

    def damage_or_heal(self, lives):
        if 0 <= self.attributes['life'] + lives <= len(self.images)-2:
            self.attributes['life'] += lives
            return True
        return False

    def paint(self, canvas):
        image = self.images[self.attributes['life']]
        if self.attributes['col'] == -1:
            image = self.images[-1]
        if self.is_death:
            image = self.images[0]
        canvas.create_image((self.attributes['col']+1.5)*Main.CELL_WIDTH, (self.attributes['row']+2.5)*Main.CELL_HEIGHT, image=image)
        for i in range(self.attributes['life']):
            canvas.create_image((i+1.5)*Main.CELL_WIDTH, 0.5*Main.CELL_HEIGHT, image=self.life_image)


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
    ADDED_ACTIONS = ['empty','move_up','move_right','move_down','move_left']

    def __init__(self):
        self.window = Tk()
        self.window.title('Cestovatel')
        self.window.resizable(False, False)
        self.frame = Frame(self.window, bg='black').pack()
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
        self.game_menu = Menu(self.canvas_bottom, tearoff=0)
        self.create_menu = Menu(self.canvas_bottom, tearoff=0)
        for operation in self.OPERATIONS:
            self.create_menu.add_command(label=self.OPERATIONS[operation]['title'], command=partial(self.add_operation, operation))
        
        self.map = []
        self.emoji = None
        self.selected_cell = None
        self.filename = None
        self.was_reset = False
        self.paint()

    def choosing_menu(self, event):
        self.selected_cell = None
        col = (event.x - self.CELL_WIDTH) // self.CELL_WIDTH
        row = (event.y - 2*self.CELL_HEIGHT) // self.CELL_HEIGHT
        if 0 <= row < len(self.map) and 0 <= col < len(self.map[row]) and self.map[row][col].is_changeable:
            self.selected_cell = self.map[row][col]
        if self.selected_cell is None:
            return
        if self.emoji is not None and self.selected_cell is not None:
            self.selected_cell.next()
        try:
            if self.emoji is None:
                self.create_menu.tk_popup(event.x_root+55, event.y_root, 0)
        finally:
            if self.emoji is None:
                self.create_menu.grab_release()
        if self.emoji is not None:
            self.paint()

    def add_operation(self, operation):
        if self.selected_cell is not None:
            if operation == 'goal':
                self.selected_cell.operations = ['goal']
            elif operation == 'empty':
                self.selected_cell.operations = []
            elif 'goal' in self.selected_cell.operations:
                self.selected_cell.operations = [operation]
            else:
                move_operations_in_selected_cell = []
                life_operations_in_selected_cell = []

                if re.match('.*move_.*', operation):
                    r_move = re.compile('.*move_.*')
                    move_operations_in_selected_cell = list(filter(r_move.match, self.selected_cell.operations))

                if re.match('.*life_.*', operation):
                    r_life = re.compile('.*life_.*')
                    life_operations_in_selected_cell = list(filter(r_life.match, self.selected_cell.operations))

                if move_operations_in_selected_cell:
                    for item in move_operations_in_selected_cell:
                        self.selected_cell.operations.remove(item)

                if life_operations_in_selected_cell:
                    for item in life_operations_in_selected_cell:
                        self.selected_cell.operations.remove(item)

                self.selected_cell.operations.append(operation)
            self.selected_cell.operations.sort()
            self.selected_cell = None
            self.paint()
    
    def reset(self):
        if self.emoji is None:
            messagebox.showinfo("Chyba", "V tvoriacom režime nevieš resetovať pohyb cestovateľa.")
        if self.emoji is not None:
            self.start_game(self.filename)
            self.was_reset = True

    def create_map(self):
        def nvl(var,val):
            if var is None:
                return val 
            return var

        rows = max(nvl(simpledialog.askinteger(title="Riadky", prompt='Počet riadkov - max 8',minvalue=1,maxvalue=8),1),1)
        cols = max(nvl(simpledialog.askinteger(title="Stĺpce", prompt='Počet stĺpcov - max 14',minvalue=1,maxvalue=14),1),1)
        self.map = []
        self.emoji = None
        for i in range(min(8,rows)):
            temp = []
            for j in range(min(14,cols)):
                temp.append(Cell(self.emoji, []))
            self.map.append(temp)
        self.paint()

    def save_map(self, filename):
        with open(filename, 'w') as file:
            json_result = '{"map": [['
            json_result += '],['.join([','.join(['{"operations": ["' + '","'.join(cell.operations) + '"]}' for cell in row]) for row in self.map])
            json_result += ']]}'
            file.write(json_result)

    def select_file_save(self):
        if self.emoji is not None:
            messagebox.showinfo("Chyba", "V hráčskom režime nevieš uložit mapu.")
            return
        was_goal = False
        for row in self.map:
            for cell in row:
                if 'goal' in cell.operations:
                    was_goal = True
                    break
        if not was_goal:
            messagebox.showinfo("Chyba", "V mape sa nenachádza Cieľ pre cestovateľa.")
            return
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".json")
        if filename is not None and filename.name:
            self.save_map(filename.name)

    def load_operations(self):
        self.OPERATIONS['empty'] = dict()
        self.OPERATIONS['empty']['title'] = 'Prázdne'
        self.OPERATIONS['empty']['attributes'] = []
        self.OPERATIONS['empty']['image'] = PhotoImage(file=PATH_IMAGES+'empty.png')
        self.OPERATIONS['goal'] = dict()
        self.OPERATIONS['goal']['title'] = 'Cieľ'
        self.OPERATIONS['goal']['attributes'] = [['is_in_goal',1]]
        self.OPERATIONS['goal']['image'] = PhotoImage(file=PATH_IMAGES+'goal.png')
        if os.path.isfile(PATH_PROJECT+'./operations.txt'):
            with open(PATH_PROJECT+'./operations.txt', 'r',encoding='utf8') as file:
                for row in file:
                    operation = row.split('#')
                    name = operation[0]
                    image_name = operation[2]
                    attributes = operation[3].split()
                    values = operation[4].split()
                    if len(attributes) == len(values) and len(values) > 0:
                        self.OPERATIONS[name] = dict()
                        self.OPERATIONS[name]['title'] = operation[1]
                        self.OPERATIONS[name]['attributes'] = []
                        self.OPERATIONS[name]['image'] = PhotoImage(file=PATH_IMAGES+image_name+'.png')
                        for i in range(len(attributes)):
                            self.OPERATIONS[name]['attributes'].append([attributes[i], int(values[i])])

    def start_game(self, filename):
        try:
            self.filename = filename
            self.map = []
            self.emoji = Emoji(3, 10)
            self.was_reset = False
            with open(filename, 'r') as file:
                loaded_json = file.read()
                json_data = json.loads(loaded_json)
                for row in json_data['map']:
                    temp = []
                    for col in row:
                        temp.append(Cell(self.emoji, col['operations']))
                    self.map.append(temp)
        except:
            messagebox.showinfo("Chyba", "Zlý vstupný súbor.")
            self.select_file()
            return
        self.paint()

    def are_all_cells_selected(self):
        for row in self.map:
            for col in row:
                if not col.operations:
                    return False
        return True

    def start_move(self):
        if self.emoji is None:
            messagebox.showinfo("Chyba", "V tvoriacom režime nevieš spustiť pohyb cestovateľa.")
        elif self.emoji.is_death:
            messagebox.showinfo("Chyba", "Cestovateľ je po smrti.")
        elif self.emoji.attributes['col'] != -1:
            messagebox.showinfo("Chyba", "Cestovateľ sa už vydal na svoju cestu.")
        elif not self.are_all_cells_selected():
            messagebox.showinfo("Chyba", "Treba zaplniť všetky prázdne bunky.")
        elif self.emoji is not None and self.emoji.attributes['col'] == -1 and self.are_all_cells_selected():
            self.emoji.attributes['row'] = 0
            self.emoji.attributes['col'] = 0
            self.map[0][0].execute_effects()
            self.was_reset = False
            self.paint()
            if self.emoji.attributes['is_in_goal'] == 1:
                messagebox.showinfo("Výhra", "Cestovateľ úspešne dorazil do cieľa.")
                return
            self.canvas_bottom.after(1000, self.animate)

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            infile = open(filename, "r")
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
            if self.emoji.attributes['is_in_goal'] == 1:
                messagebox.showinfo("Výhra", "Cestovateľ úspešne dorazil do cieľa.")
                return
            if self.emoji.attributes['life'] <= 0:
                messagebox.showinfo("Smrť", "Cestovateľ zomrel po ceste do cieľa.")
                return
            if self.emoji.attributes['row'] <= -1 or self.emoji.attributes['row'] >= len(self.map) or self.emoji.attributes['col'] <= -1 or self.emoji.attributes['col'] >= len(self.map[0]):
                self.emoji.is_death = True
                self.paint()
                messagebox.showinfo("Pokus o útek", "Cestovateľ utiekol po ceste do cieľa.")
                return
            self.canvas_bottom.after(1000, self.animate)   
    
    def paint(self):
        self.canvas_bottom.delete('all')
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j].is_changeable:
                    self.canvas_bottom.create_rectangle((j+1)*self.CELL_WIDTH, (i+2)*self.CELL_HEIGHT, (j+2)*self.CELL_WIDTH, (i+3)*self.CELL_HEIGHT, fill='yellowgreen')
                else:
                    self.canvas_bottom.create_rectangle((j+1)*self.CELL_WIDTH, (i+2)*self.CELL_HEIGHT, (j+2)*self.CELL_WIDTH, (i+3)*self.CELL_HEIGHT, fill='dodgerblue')
                for operation in self.map[i][j].operations:
                    self.canvas_bottom.create_image((j+1.5)*self.CELL_WIDTH, (i+2.5)*self.CELL_HEIGHT, image=self.OPERATIONS[operation]['image'])
                if not self.map[i][j].operations:
                    self.canvas_bottom.create_image((j+1.5)*self.CELL_WIDTH, (i+2.5)*self.CELL_HEIGHT, image=self.OPERATIONS['empty']['image'])
        if self.emoji is not None:
            self.emoji.paint(self.canvas_bottom)


if __name__ == "__main__":
    m = Main()
    m.window.mainloop()
