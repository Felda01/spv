from tkinter import *
from tkinter import filedialog
import os


class Item:
    def __init__(self, color: str, name=''):
        self.name = name
        self.color = color
        self.focus = False
        self.focus_border_color = '#FF0000'

    def draw_item(self, canvas: Canvas):
        pass

    def draw_info(self, canvas: Canvas):
        pass


class Person(Item):
    def __init__(self, x: int, y: int, color: str, name=''):
        super().__init__(color, name)
        self.x = x
        self.y = y

    def move(self, event: Event):
        pass

    def draw_item(self, canvas: Canvas):
        pass

    def draw_info(self, canvas: Canvas):
        super().draw_info(canvas)

    def load(self, properties: dict):
        super().name = properties['name']
        super().color = properties['color']
        self.x = properties['x']
        self.y = properties['y']

    def save(self, uid: int):
        string_properties = ';'.join(['type=person', 'uid=' + str(uid), 'name=' + super().name, 'x=' + str(self.x),
                                      'y=' + str(self.y), 'color=' + super().color])
        hash_properties = hash(string_properties)

        return string_properties + ';hash=' + str(hash_properties)


class Relation(Item):
    def __init__(self, color: str, parent: Person, child: Person, name=''):
        super().__init__(color, name)
        self.parent = parent
        self.child = child

    def draw_info(self, canvas: Canvas):
        super().draw_info(canvas)

    def draw_item(self, canvas: Canvas):
        pass

    def load(self, properties: dict):
        super().name = properties['name']
        super().color = properties['color']
        self.parent = properties['parent']
        self.child = properties['child']

    def save(self, uid_parent: int, uid_child: int):
        string_properties = ';'.join(['type=relation', 'uid_parent=' + str(uid_parent), 'uid_child=' + str(uid_child),
                                      'name=' + super().name, 'color=' + super().color])
        hash_properties = hash(string_properties)

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

    def __init__(self):
        self.window = Tk()
        self.window.title('Burgraren')
        self.window.resizable(False, False)
        self.frame = Frame(self.window, bg='black').pack()
        # TOP
        self.canvas_top = Canvas(self.frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # LEFT
        self.canvas_left = Canvas(self.frame, width=self.LEFT_WIDTH, height=self.LEFT_HEIGHT, bg='#bada55',
                                  scrollregion=(0, 0, self.LEFT_WIDTH, self.LEFT_HEIGHT))
        self.canvas_left.pack(side=LEFT, expand=False)

        # RIGHT
        self.canvas_right = Canvas(self.frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT, bg='lightblue')
        self.canvas_right.pack(side=RIGHT, expand=False)
        b = Button(self.canvas_top, text='Načítaj súbor', command=self.select_file)
        b.place(x=10, y=10)
        b = Button(self.canvas_top, text='Ulož Slovo', command=self.save)
        b.place(x=100, y=10)
        b = Button(self.canvas_top, text='Export', command=self.export)
        b.place(x=200, y=10)

        self.graph = dict()
        self.selected_item = None

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            self.load(filename)

    def load(self, file_name: str):
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                row = file.readline().strip()
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
                    current_row_hash = hash(';'.join("{!s}={!r}".format(key, value) for (key, value) in properties.items()))
                    if str(old_row_hash) != str(current_row_hash):
                        continue

    def save(self, file_name: str):
        pass

    def export(self):
        pass

    def delete_canvas(self):
        pass

    def click(self, event: Event):
        pass

    def add_relation(self, what):
        pass

    def add_person(self):
        pass


if __name__ == '__main__':
    m = Main()
    m.window.mainloop()
