from tkinter import *
from tkinter import filedialog
import os
import uuid
import hashlib


class Item:
    def __init__(self, color: str, name=''):
        self.name = name
        self.color = color
        self.focus = False
        self.focus_border_color = '#FF0000'

    def draw_item(self, canvas: Canvas):
        pass

    def draw_info(self, canvas: Canvas):
        canvas.delete('all')

        canvas.create_text(10, 10, text='Meno')
        canvas.create_text(Main.LEFT_WIDTH // 2 + 10, 10, text=self.name)

        canvas.create_text(10, 10, text='Farba')
        canvas.create_rectangle(Main.LEFT_WIDTH // 2 + 10, 60, Main.LEFT_WIDTH - 10, 100, fill=self.color, outline='black', width=3)


class Person(Item):
    def __init__(self, x=0, y=0, color='', name='', uid=''):
        super().__init__(color, name)
        self.x = x
        self.y = y
        self.a = len(name) # set x-radius
        self.b = 20        # set y-radius
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
                           fill=self.color, outline=outline)
        canvas.create_text(self.x, self.y, text=self.name)

    def draw_info(self, canvas: Canvas):
        super().draw_info(canvas)

    def load(self, properties: dict):
        self.name = properties['name']
        self.color = properties['color']
        self.x = properties['x']
        self.y = properties['y']

    def save(self):
        string_properties = ';'.join(['type=person', 'uid=' + str(self.uid), 'name=' + super().name, 'x=' + str(self.x),
                                      'y=' + str(self.y), 'color=' + super().color])
        hash_properties = hash(string_properties)

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
        self.name = properties['name']
        self.color = properties['color']
        self.parent = properties['parent']
        self.child = properties['child']

    def save(self, uid_parent: str, uid_child: str):
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
        filename = filedialog.askopenfilename()
        if filename:
            self.load(filename)
            print(self.graph)

    def load(self, file_name: str):
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
        pass

    def export(self):
        pass

    def delete_canvas(self):
        pass

    def click(self, event: Event):
        pass

    def add_relation(self, relation: Relation):
        if relation.parent in self.graph and relation.child in self.graph:
            if relation not in self.graph[relation.parent]:
                self.graph[relation.parent].append(relation)
            if relation not in self.graph[relation.child]:
                self.graph[relation.child].append(relation)

    def add_person(self, person: Person):
        if person not in self.graph:
            self.graph[person] = list()


if __name__ == '__main__':
    m = Main()
    m.window.mainloop()
