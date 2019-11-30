from tkinter import *
from tkinter import filedialog
import os
import uuid
import hashlib
from functools import partial
import re


class Item:
    def __init__(self, color: str, name=''):
        self.name = name
        self.color = color
        self.focus = False
        self.focus_border_color = '#FF0000'

    def draw_item(self, canvas: Canvas):
        pass

    def draw_info(self, canvas: Canvas):
        if not self.focus:
            return

        canvas.create_text(30, 50, text='Meno', anchor=NW, fill='green', font=Main.FONT_STYLE)
        canvas.create_text(Main.LEFT_WIDTH // 2 + 10, 50, text=self.name, anchor=NW, fill='white', font=Main.FONT_STYLE)

        canvas.create_text(30, 75, text='Farba', anchor=NW, fill='green', font=Main.FONT_STYLE)
        canvas.create_rectangle(Main.LEFT_WIDTH // 2 + 10, 80, Main.LEFT_WIDTH - 30, 95, fill=self.color, outline='black', width=3)


class Person(Item):
    def __init__(self, x=0, y=0, color='', name='', uid=''):
        super().__init__(color, name)
        self.x = x
        self.y = y
        self.a = 7*len(self.name) # set x-radius
        self.b = 20               # set y-radius
        if uid:
            self.uid = uid
        else:
            self.uid = uuid.uuid4()

    def move(self, event: Event):
        pass

    def draw_item(self, canvas: Canvas):
        outline = 'black'
        if self.focus:
            outline = self.focus_border_color
        canvas.create_oval(self.x - self.a, self.y - self.b, self.x + self.a, self.y + self.b,
                           fill=self.color, outline=outline, width=2)
        canvas.create_text(self.x, self.y, text=self.name, font=Main.FONT_STYLE)

    def draw_info(self, canvas: Canvas):
        super().draw_info(canvas)

    def is_click_in(self, event):
        return ((event.x-self.x)**2)/self.a**2 + ((event.y-self.y)**2)/self.b**2 <= 1.0

    def load(self, properties: dict):
        self.__init__(int(properties['x']), int(properties['y']), properties['color'], properties['name'])

    def save(self):
        string_properties = ';'.join(['type=person', 'uid=' + str(self.uid), 'name=' + self.name, 'x=' + str(self.x),
                                      'y=' + str(self.y), 'color=' + self.color])
        hash_properties = hashlib.sha1(string_properties.encode()).hexdigest()

        return string_properties + ';hash=' + str(hash_properties)


class Relation(Item):
    def __init__(self, color='', parent=None, child=None, name=''):
        super().__init__(color, name)
        self.parent = parent
        self.child = child

    def draw_info(self, canvas: Canvas):
        super().draw_info(canvas)

    def draw_item(self, canvas: Canvas):
        pass

    def load(self, properties: dict):
        self.__init__(properties['color'], properties['parent'], properties['child'], properties['name'])

    def save(self):
        string_properties = ';'.join(['type=relation', 'parent=' + str(self.parent.uid), 'child=' + str(self.child.uid),
                                      'name=' + self.name, 'color=' + self.color])
        hash_properties = hashlib.sha1(string_properties.encode()).hexdigest()

        return string_properties + ';hash=' + str(hash_properties)


class Main:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    TOP_WIDTH = WINDOW_WIDTH
    TOP_HEIGHT = 50
    LEFT_WIDTH = 250
    LEFT_HEIGHT = WINDOW_HEIGHT - TOP_HEIGHT
    RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH
    RIGHT_HEIGHT = WINDOW_HEIGHT - TOP_HEIGHT
    FONT_STYLE = 'system 15 bold'
    COLORS_DEFAULT = ['white', 'green', 'blue', 'orange', 'brown', 'grey', 'gold']
    CONFIG_COLORS_FILE = './config/colors.txt'

    def __init__(self):
        self.window = Tk()
        self.window.title('Rodostrom')
        self.window.resizable(False, False)
        self.window.configure(bg='black')
        self.frame = Frame(self.window, bg='black').pack()
        # TOP
        self.canvas_top = Canvas(self.frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # LEFT
        self.canvas_left = Canvas(self.frame, width=self.LEFT_WIDTH, height=self.LEFT_HEIGHT,
                                  scrollregion=(0, 0, self.LEFT_WIDTH, self.LEFT_HEIGHT))
        self.canvas_left.pack(side=LEFT, expand=False)

        # RIGHT
        self.canvas_right = Canvas(self.frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT)
        self.canvas_right.pack(side=RIGHT, expand=False)

        # BINDINGS
        self.canvas_right.bind('<Button-1>', self.click)
        self.canvas_right.bind('<B1-Motion>', self.move)
        self.canvas_right.bind('<ButtonPress-1>', self.start_move)
        self.canvas_right.bind('<ButtonRelease-1>', self.end_move)

        # IMAGES
        self.background_right = PhotoImage(file='images/background.png')
        self.background_left = PhotoImage(file='images/background_left.png')
        b = Button(self.canvas_top, text='Načítaj rodostrom', command=self.select_file_load)
        b.place(x=10, y=13)
        b = Button(self.canvas_top, text='Ulož rodostrom', command=self.select_file_save)
        b.place(x=120, y=13)
        b = Button(self.canvas_top, text='Obrázok', command=self.export)
        b.place(x=217, y=13)

        self.graph = dict()
        self.selected_item = None
        self.picked = []
        self.moving_object = None
        self.colors = []

        self.paint_graph()
        self.load_colors()
        self.draw_color_picker()

    def select_file_load(self):
        filename = filedialog.askopenfilename()
        if filename:
            #TODO: ak existuje graf, opytat sa ci chce aktualny zahodit a otvorit novy
            self.load(filename)
        self.paint_graph()

    def select_file_save(self):
        filename = filedialog.asksaveasfilename()
        if filename:
            self.save(filename)

    def load(self, file_name: str):
        self.graph = dict()
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                row = file.readline().strip()
                uid_persons = dict()
                while row != '':
                    row_items = row.split(';')
                    properties = dict()
                    old_row_hash = ''
                    for item in row_items:
                        key, value = item.split('=')
                        if key == 'hash':
                            old_row_hash = value
                        else:
                            properties[key] = value

                    string_properties = ';'.join("{s}={r}".format(s=key, r=value) for (key, value) in properties.items())
                    current_row_hash = hashlib.sha1(string_properties.encode()).hexdigest()
                    if str(old_row_hash) != str(current_row_hash):
                        row = file.readline().strip()
                        continue

                    if properties['type'] == 'person':
                        person = Person()
                        person.load(properties)
                        uid_persons[str(properties['uid'])] = person
                        self.add_person(person)

                    if properties['type'] == 'relation':
                        relation = Relation()
                        if uid_persons[str(properties['parent'])] and uid_persons[str(properties['child'])]:
                            properties['parent'] = uid_persons[str(properties['parent'])]
                            properties['child'] = uid_persons[str(properties['child'])]
                            relation.load(properties)
                            self.add_relation(relation)
                        else:
                            row = file.readline().strip()
                            continue
                    row = file.readline().strip()

    def save(self, file_name: str):
        persons = set()
        relations = set()

        for person in self.graph:
            persons.add(person)
            person_relations = self.graph[person]
            for relation in person_relations:
                relations.add(relation)

        if os.path.isfile(file_name):
            with open(file_name, 'w') as file:
                for person in persons:
                    file.write(person.save() + '\n')

                for relation in relations:
                    file.write(relation.save() + '\n')

    def export(self):
        pass

    def delete_canvas(self):
        self.canvas_right.delete('all')
        self.canvas_right.create_image(0,0,image=self.background_right,anchor=NW)
        self.canvas_left.delete('all')
        self.canvas_left.create_image(0, 0, image=self.background_left, anchor=NW)
        pass

    def click(self, event: Event):
        for person in self.graph.keys():
            if person.is_click_in(event):
                person.focus = not person.focus
                if person.focus:
                    self.picked.append(person)
                else:
                    self.picked.remove(person)
        self.paint_graph()

    def paint_graph(self):
        self.delete_canvas()
        for person in self.graph.keys():
            person.draw_item(self.canvas_right)
        if len(self.picked) > 0:
            self.picked[-1].draw_info(self.canvas_left)

    def draw_color_picker(self):
        x = 25
        y = 365
        r = None
        for color in self.colors:
            btn = Button(master=self.canvas_left, command=partial(self.set_color, color), bg=color, width=5, height=2)
            btn.place(x=x, y=y)
            x += 50
            if x + 50 >= self.LEFT_WIDTH:
                x = 25
                y += 50

    def set_color(self, color):
        for person in self.graph.keys():
            if person.focus:
                person.color = color
        self.paint_graph()

    def add_relation(self, relation: Relation):
        if relation.parent in self.graph and relation.child in self.graph:
            if relation not in self.graph[relation.parent]:
                self.graph[relation.parent].append(relation)
            if relation not in self.graph[relation.child]:
                self.graph[relation.child].append(relation)

    def add_person(self, person: Person):
        if person not in self.graph:
            self.graph[person] = list()

    def move(self, event):
        deltax = event.x - self.moving_object.x
        deltay = event.y - self.moving_object.y
        self.moving_object.x += deltax
        self.moving_object.y += deltay
        self.x = event.x
        self.y = event.y
        self.paint_graph()

    def start_move(self, event):
        self.moving_object = None
        for person in self.graph.keys():
            if person.is_click_in(event):
                self.moving_object = person
                person.focus = not person.focus
                if person.focus:
                    self.picked.append(person)
                else:
                    self.picked.remove(person)
        self.paint_graph()

    def end_move(self, event):
        self.moving_object = None

    def load_colors(self):
        self.colors = []
        if os.path.isfile(self.CONFIG_COLORS_FILE):
            with open(self.CONFIG_COLORS_FILE, 'r') as file:
                row = file.readline().strip()
                while row != '':
                    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', row)
                    if match:
                        self.colors.append(row)
                    row = file.readline().strip()

        if not self.colors:
            self.colors = self.COLORS_DEFAULT


if __name__ == '__main__':
    m = Main()
    m.window.mainloop()
