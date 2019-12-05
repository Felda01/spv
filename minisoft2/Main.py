from tkinter import *
from tkinter import filedialog
import os
import uuid
from functools import partial
import re
import json


class Item:
    def __init__(self, color: str, name=''):
        self.name = name
        self.color = color
        self.focus = False
        self.focus_border_color = '#FF0000'
        self.s = StringVar()
        self.entry = None

    def draw_item(self, canvas: Canvas):
        pass

    def draw_info(self, canvas: Canvas):
        if not self.focus:
            return

        self.entry = Entry(master=canvas, text=self.name, font=Main.FONT_STYLE, width=8, textvariable=self.s)
        self.entry.place(x=Main.LEFT_WIDTH // 2 + 15, y=50)
        self.entry.delete(0, END)
        self.entry.insert(0, self.name)
        self.entry.focus_set()
        canvas.create_text(30, 50, text='Meno', anchor=NW, fill='green', font=Main.FONT_STYLE)

        canvas.create_text(30, 80, text='Farba', anchor=NW, fill='green', font=Main.FONT_STYLE)
        canvas.create_rectangle(Main.LEFT_WIDTH // 2 + 10, 85, Main.LEFT_WIDTH - 30, 100, fill=self.color, outline='black', width=3)


class Person(Item):
    def __init__(self, x=0, y=0, color='', name='', uid=''):
        super().__init__(color, name)
        self.x = x
        self.y = y
        self.a = 7 * len(self.name)  # set x-radius
        self.b = 20                  # set y-radius
        self.entry = None
        if uid:
            self.uid = uid
        else:
            self.uid = uuid.uuid4()

    def move(self, event: Event):
        pass

    def draw_item(self, canvas: Canvas):
        outline = self.color
        if self.focus:
            outline = self.focus_border_color
        canvas.create_oval(self.x - self.a, self.y - self.b, self.x + self.a, self.y + self.b,
                           fill=self.color, outline=outline, width=2)
        canvas.create_text(self.x, self.y, text=self.name, font=Main.FONT_STYLE)

    def draw_info(self, canvas: Canvas):
        canvas.create_text(Main.LEFT_WIDTH // 2, 28, text='OSOBA', fill='green', font=Main.FONT_STYLE)

        super().draw_info(canvas)

        canvas.create_text(30, 110, text='Pozícia X', anchor=NW, fill='blue', font=Main.FONT_STYLE)
        canvas.create_text(Main.LEFT_WIDTH // 2 + 10, 110, text=str(self.x), anchor=NW, fill='white', font=Main.FONT_STYLE)

        canvas.create_text(30, 140, text='Pozícia y', anchor=NW, fill='blue', font=Main.FONT_STYLE)
        canvas.create_text(Main.LEFT_WIDTH // 2 + 10, 140, text=str(self.y), anchor=NW, fill='white', font=Main.FONT_STYLE)

    def is_click_in(self, event):
        return ((event.x-self.x)**2)/self.a**2 + ((event.y-self.y)**2)/self.b**2 <= 1.0

    def load(self, properties: dict):
        if 'x' not in properties or 'y' not in properties or 'color' not in properties or 'name' not in properties or 'uid' not in properties:
            return False
        self.__init__(int(properties['x']), int(properties['y']), properties['color'], properties['name'], properties['uid'])
        return True

    def save(self):
        return '{"uid" : "' + str(self.uid) + '", "x" : "' + str(self.x) + '","y" : "' + str(self.y) + '","name" : "' + self.name + '","color" : "' + self.color + '"}'

    def change(self):
        if self.entry is not None:
            self.entry.place_forget()
        if self.s.get() != '':
            self.name = self.s.get()
            self.a = 7 * len(self.name)  # set x-radius


class Relation(Item):
    def __init__(self, color='', parent=None, child=None, name='', uid=''):
        super().__init__(color, name)
        self.parent = parent
        self.child = child
        if uid:
            self.uid = uid
        else:
            self.uid = uuid.uuid4()

    def draw_info(self, canvas: Canvas):
        canvas.create_text(Main.LEFT_WIDTH // 2, 28, text='VZTAH', fill='green', font=Main.FONT_STYLE)

        super().draw_info(canvas)

    def switch(self):
        self.parent, self.child = self.child, self.parent

    def draw_item(self, canvas: Canvas):
        parent_x = self.parent.x
        parent_y = self.parent.y
        child_x = self.child.x
        child_y = self.child.y
        if parent_x + self.parent.a < child_x - self.child.a:
            parent_x += self.parent.a
        elif parent_x - self.parent.a > child_x + self.child.a:
            parent_x -= self.parent.a
        else:
            if parent_y > child_y:
                parent_y -= self.parent.b
            else:
                parent_y += self.parent.b

        if child_x + self.child.a < self.parent.x - self.parent.a:
            child_x += self.child.a
        elif child_x - self.child.a > self.parent.x + self.parent.a:
            child_x -= self.child.a
        else:
            if self.parent.y < child_y:
                child_y -= self.child.b
            else:
                child_y += self.child.b
        color = self.color
        if self.focus:
            color = self.focus_border_color
        canvas.create_line(parent_x, parent_y, child_x, child_y, width=3, arrow=LAST, arrowshape=(20, 40, 10), fill=color)
        canvas.create_text((self.parent.x+self.child.x)/2, (self.parent.y+self.child.y)/2, text=self.name, font=Main.FONT_STYLE, fill='crimson', angle=-45)

    def load(self, properties: dict):
        if 'color' not in properties or 'parent' not in properties or 'child' not in properties or 'name' not in properties or 'uid' not in properties:
            return False
        self.__init__(properties['color'], properties['parent'], properties['child'], properties['name'], properties['uid'])
        return True

    def save(self):
        return '{"uid" : "' + str(self.uid) + '", "parent" : "' + str(self.parent.uid) + '","child" : "' + str(self.child.uid) + '","name" : "' + self.name + '","color" : "' + self.color + '"}'

    def click_distance(self, event):
        if min(self.parent.x, self.child.x) > event.x or max(self.parent.x, self.child.x) < event.x or min(self.parent.y, self.child.y) > event.y or max(self.parent.y, self.child.y) < event.y:
            return 1000
        n_vector = (-self.parent.y+self.child.y, self.parent.x - self.child.x)
        c = -n_vector[0]*self.parent.x-n_vector[1]*self.parent.y
        return abs((n_vector[0]*event.x+n_vector[1]*event.y+c)/((n_vector[0]**2+n_vector[1]**2)**0.5))

    def change(self):
        if self.s.get() != '':
            self.name = self.s.get()
            self.entry.place_forget()


class Exercise:
    def __init__(self, story_text='', question='', graph_file='', answers=None, uid=''):
        self.story_text = story_text
        self.question = question
        self.graph_file = graph_file
        self.graph = dict()
        self.graph['persons'] = dict()
        self.graph['relations'] = dict()
        self.objects = []
        if answers:
            self.answers = answers
        else:
            self.answers = set()

        if uid:
            self.uid = uid
        else:
            self.uid = uuid.uuid4()
        if self.graph_file != '':
            self.load_graph()

    def draw_exercise(self, canvas):
        w = Message(canvas, text=self.story_text, bg='white', width=180, font=Main.FONT_STYLE)
        w.place(x=30,y=50)
        self.objects.append(w)
        w = Message(canvas, text=self.question, bg='white', width=180, font=Main.FONT_STYLE)
        w.place(x=30, y=230)
        self.objects.append(w)

    def remove_all_objects(self):
        for item in self.objects:
            item.place_forget()

    def load_graph(self):
        if os.path.isfile(self.graph_file):
            with open(self.graph_file, 'r', encoding='utf8') as file:
                loaded_graph_json = file.read()
                graph_data = json.loads(loaded_graph_json)
                uid_persons = dict()

                for person_data in graph_data['persons']:
                    person = Person()
                    correct = person.load(person_data)
                    if correct:
                        uid_persons[str(person_data['uid'])] = person
                        self.add_person(person)

                for relation_data in graph_data['relations']:
                    relation = Relation()
                    if uid_persons[str(relation_data['parent'])] and uid_persons[str(relation_data['child'])]:
                        relation_data['parent'] = uid_persons[str(relation_data['parent'])]
                        relation_data['child'] = uid_persons[str(relation_data['child'])]
                        correct = relation.load(relation_data)
                        if correct:
                            self.add_relation(relation)

    def add_relation(self, relation: Relation):
        if relation.uid not in self.graph['relations']:
            self.graph['relations'][str(relation.uid)] = relation

    def add_person(self, person: Person):
        if person.uid not in self.graph['persons']:
            self.graph['persons'][str(person.uid)] = person

    def load(self, properties):
        if 'uid' not in properties or 'story_text' not in properties or 'question' not in properties or 'graph_file' not in properties or 'answers' not in properties:
            return False
        answers = []
        for answer in properties['answers']:
            answers.append(answer)
        self.__init__(properties['story_text'], properties['question'], properties['graph_file'], answers, properties['uid'])
        return True

    def save(self):
        def get_answers(answers):
            result = '['
            i = 0
            for answer in answers:
                if i != 0:
                    result += ','
                result += '"' + str(answer) + '"'
                i += 1
            result += ']'
            return result

        return '{"uid" : "' + str(self.uid) + '", "story_text" : "' + self.story_text + '","question" : "' + self.question + '","graph_file" : "' + str(self.graph_file) + '","answers" : ' + get_answers(self.answers) + '}'

    def evaluate(self):
        result = set()
        for person_uid in self.graph['persons']:
            person = self.graph['persons'][person_uid]
            if person.focus:
                result.add(str(person.uid))
        for relation_uid in self.graph['relations']:
            relation = self.graph['relations'][relation_uid]
            if relation.focus:
                result.add(str(relation.uid))

        return result == self.answers


class Test:
    def __init__(self, title=''):
        self.title = title
        self.exercises = []
        self.actual_question = 0
        self.mode = 'testing'

    def load(self, file_name: str):
        if os.path.isfile(file_name):
            with open(file_name, 'r', encoding='utf8') as file:
                loaded_test_json = file.read()
                test_data = json.loads(loaded_test_json)
                if 'title' in test_data:
                    self.title = test_data['title']
                if 'exercises' in test_data:
                    for exercise_data in test_data['exercises']:
                        exercise = Exercise()
                        correct = exercise.load(exercise_data)
                        if correct:
                            self.exercises.append(exercise)

    def save(self, file_name):
        with open(file_name, 'w', encoding='utf8') as file:
            result_json = '{"title": "' + self.title + '", "exercises": ['
            result_json += ','.join([exercise.save() for exercise in self.exercises])
            result_json += ']}'
            file.write(result_json)

    def get_question(self, canvas):
        if self.mode == 'testing' and len(self.exercises) > 0:
            self.exercises[self.actual_question].draw_exercise(canvas)
            return self.exercises[self.actual_question].graph

    def next_question(self):
        if self.actual_question + 1 >= len(self.exercises):
            return
        self.exercises[self.actual_question].remove_all_objects()
        self.actual_question += 1

    def previous_question(self):
        if self.actual_question - 1 < 0:
            return
        self.exercises[self.actual_question].remove_all_objects()
        self.actual_question -= 1

    def evaluate(self):
        result = dict()
        result['correct'] = []
        result['wrong'] = []
        for exercise in self.exercises:
            if exercise.evaluate():
                result['correct'].append(exercise)
            else:
                result['wrong'].append(exercise)
        return result


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
        self.canvas_left = Canvas(self.frame, width=self.LEFT_WIDTH, height=self.LEFT_HEIGHT)
        self.canvas_left.pack(side=LEFT, expand=False)

        # RIGHT
        self.canvas_right = Canvas(self.frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT)
        self.canvas_right.pack(side=RIGHT, expand=False)

        # IMAGES
        self.background_right = PhotoImage(file='images/background.png')
        self.background_left = PhotoImage(file='images/background_left.png')

        # BINDINGS
        self.canvas_right.bind('<ButtonPress-1>', self.start_move)
        self.canvas_right.bind('<ButtonRelease-1>', self.end_move)

        # INITIALIZATION
        self.graph = dict()
        self.graph['persons'] = dict()
        self.graph['relations'] = dict()
        self.picked = []
        self.moving_object = None
        self.operation = None
        self.colors = []
        self.mode = ''
        self.buttons = []
        self.operations = dict()

        self.load_colors()
        self.init_for_testing()
        self.paint_graph()

    def init_for_creating(self):
        if self.test is not None:
            self.test.exercises[self.test.actual_question].remove_all_objects()
            self.test = None
        self.mode = 'creating'
        for button in self.buttons:
            button.place_forget()
        self.buttons = []
        # BINDINGS
        self.canvas_right.bind('<B1-Motion>', self.move)

        # BUTTONS
        switch_btn = Button(self.canvas_left, text='Vymeň', command=self.switch)
        switch_btn.place(x=self.LEFT_WIDTH - 80, y=230)
        self.buttons.append(switch_btn)
        self.operations = dict()
        self.operations['create_person'] = Button(master=self.canvas_right, text='Pridaj osobu', width=12,
                                                  command=partial(self.set_operation, 'create_person'), bg='white')
        self.operations['create_person'].place(x=10, y=self.RIGHT_HEIGHT - 150)
        self.operations['create_relationship'] = Button(master=self.canvas_right, text='pridaj vztah', width=12,
                                                        command=partial(self.set_operation, 'create_relationship'),
                                                        bg='white')
        self.operations['create_relationship'].place(x=10, y=self.RIGHT_HEIGHT - 100)
        self.operations['moving'] = Button(master=self.canvas_right, text='posuvaj osobu', width=12,
                                           command=partial(self.set_operation, 'moving'), bg='white')
        self.operations['moving'].place(x=10, y=self.RIGHT_HEIGHT - 50)
        b = Button(self.canvas_top, text='Načítaj rodostrom', command=self.select_file_load)
        b.place(x=10, y=13)
        self.buttons.append(b)
        b = Button(self.canvas_top, text='Ulož rodostrom', command=self.select_file_save)
        b.place(x=120, y=13)
        self.buttons.append(b)
        b = Button(self.canvas_top, text='Obrázok', command=self.export)
        b.place(x=217, y=13)
        self.buttons.append(b)
        b = Button(self.canvas_top, text='Testovaci rezim', command=self.init_for_testing)
        b.place(x=278, y=13)
        self.buttons.append(b)
        self.draw_color_picker()
        self.delete_canvas()

    def init_for_testing(self):
        self.mode = 'testing'
        self.test = None
        for button in self.buttons + list(self.operations.values()):
            button.place_forget()
        self.buttons = []
        self.canvas_right.unbind('<B1-Motion>')
        b = Button(self.canvas_top, text='Načítaj pribeh', command=self.select_file_load)
        b.place(x=10, y=13)
        self.buttons.append(b)
        b = Button(self.canvas_top, text='Tvoriaci režim', command=self.init_for_creating)
        b.place(x=100, y=13)
        self.buttons.append(b)
        b = Button(self.canvas_left, text='<', command=self.previous_question, font=Main.FONT_STYLE)
        b.place(x=Main.LEFT_WIDTH // 2 - 45, y=Main.LEFT_HEIGHT // 2)
        self.buttons.append(b)
        b = Button(self.canvas_left, text='>', command=self.next_question, font=Main.FONT_STYLE)
        b.place(x=Main.LEFT_WIDTH // 2 + 20, y=Main.LEFT_HEIGHT // 2)
        self.buttons.append(b)
        self.delete_canvas()

    def next_question(self):
        if self.test is not None:
            self.test.next_question()
            self.graph = self.test.get_question(self.canvas_left)
            self.paint_graph()

    def previous_question(self):
        if self.test is not None:
            self.test.previous_question()
            self.graph = self.test.get_question(self.canvas_left)
            self.paint_graph()

    def switch(self):
        for item in self.picked:
            if isinstance(item, Relation):
                item.switch()
        self.paint_graph()

    def select_file_load(self):
        filename = filedialog.askopenfilename()
        if filename:
            #TODO: ak existuje graf, opytat sa ci chce aktualny zahodit a otvorit novy
            if self.mode == 'creating':
                self.load(filename)
            else:
                self.test = Test()
                self.test.load(filename)
                self.graph = self.test.get_question(self.canvas_left)
        self.paint_graph()

    def select_file_save(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".json")
        if filename is not None and filename.name:
            self.save(filename.name)

    def load(self, file_name: str):
        if os.path.isfile(file_name):
            with open(file_name, 'r', encoding='utf8') as file:
                loaded_graph_json = file.read()
                graph_data = json.loads(loaded_graph_json)
                uid_persons = dict()

                for person_data in graph_data['persons']:
                    person = Person()
                    correct = person.load(person_data)
                    if correct:
                        uid_persons[str(person_data['uid'])] = person
                        self.add_person(person)

                for relation_data in graph_data['relations']:
                    relation = Relation()
                    if uid_persons[str(relation_data['parent'])] and uid_persons[str(relation_data['child'])]:
                        relation_data['parent'] = uid_persons[str(relation_data['parent'])]
                        relation_data['child'] = uid_persons[str(relation_data['child'])]
                        correct = relation.load(relation_data)
                        if correct:
                            self.add_relation(relation)

    def save(self, file_name: str):
        if os.path.isfile(file_name):
            with open(file_name, 'w', encoding='utf8') as file:
                result_json = '{"persons": ['

                result_json += ','.join([self.graph['persons'][person_uid].save() for person_uid in self.graph['persons']])
                result_json += '], "relations" : ['

                result_json += ','.join([self.graph['relations'][relation_uid].save() for relation_uid in self.graph['relations']])
                result_json += ']}'

                file.write(result_json)

    def export(self):
        pass

    def delete_canvas(self):
        self.canvas_right.delete('all')
        self.canvas_right.create_image(0,0,image=self.background_right,anchor=NW)
        self.canvas_left.delete('all')
        self.canvas_left.create_image(0, 0, image=self.background_left, anchor=NW)

    def paint_graph(self):
        if self.graph['persons'] is None:
            return
        self.delete_canvas()
        for person_uid in self.graph['persons']:
            self.graph['persons'][person_uid].draw_item(self.canvas_right)
        for relation_uid in self.graph['relations']:
            self.graph['relations'][relation_uid].draw_item(self.canvas_right)

        if self.mode == 'creating' and len(self.picked) > 0:
            self.picked[-1].draw_info(self.canvas_left)


    def draw_color_picker(self):
        x = 25
        y = 365
        r = None
        for color in self.colors:
            btn = Button(master=self.canvas_left, command=partial(self.set_color, color), bg=color, width=5, height=2)
            btn.place(x=x, y=y)
            self.buttons.append(btn)
            x += 50
            if x + 50 >= self.LEFT_WIDTH:
                x = 25
                y += 50

    def set_color(self, color):
        for item in self.picked:
            item.color = color
            item.focus = False
            self.picked.remove(item)
            item.change()
        self.paint_graph()

    def add_relation(self, relation: Relation):
        if relation.uid not in self.graph['relations']:
            self.graph['relations'][str(relation.uid)] = relation

    def add_person(self, person: Person):
        if person.uid not in self.graph['persons']:
            self.graph['persons'][str(person.uid)] = person

    def move(self, event):
        if self.moving_object is not None:
            self.remove_all_focuses()
            self.moving_object.focus = True
            deltax = event.x - self.moving_object.x
            deltay = event.y - self.moving_object.y
            self.moving_object.x += deltax
            self.moving_object.y += deltay
            self.x = event.x
            self.y = event.y
            self.paint_graph()
            self.moving_object.draw_info(self.canvas_left)

    def start_move(self, event):
        if self.mode == 'testing':
            picked = False
            for person_uid in self.graph['persons']:
                person = self.graph['persons'][person_uid]
                if person.is_click_in(event):
                    person.focus = not person.focus
                    if person.focus:
                        self.picked.append(person)
                    else:
                        if person in self.picked:
                            self.picked.remove(person)
                    picked = True
            if not picked:
                for relation_uid in self.graph['relations']:
                    relation = self.graph['relations'][relation_uid]
                    if relation.click_distance(event) < 15:
                        relation.focus = not relation.focus
                        if relation.focus:
                            self.picked.append(relation)
                        else:
                            if relation in self.picked:
                                self.picked.remove(relation)
        else:
            for item in self.picked:
                item.change()
            if self.operation is None:
                self.remove_all_focuses()
                picked = False
                for person_uid in self.graph['persons']:
                    person = self.graph['persons'][person_uid]
                    if person.is_click_in(event):
                        person.focus = not person.focus
                        if person.focus:
                            self.picked.append(person)
                        else:
                            if person in self.picked:
                                self.picked.remove(person)
                        picked = True
                if not picked:
                    for relation_uid in self.graph['relations']:
                        relation = self.graph['relations'][relation_uid]
                        if relation.click_distance(event) < 15:
                            relation.focus = not relation.focus
                            if relation.focus:
                                self.picked.append(relation)
                            else:
                                if relation in self.picked:
                                    self.picked.remove(relation)
            elif self.operation == 'create_person':
                self.remove_all_focuses()
                person = Person(x=event.x, y=event.y, color='white', name='Zadaj meno')
                self.add_person(person)
            elif self.operation == 'moving':
                self.remove_all_focuses()
                self.moving_object = None
                for person_uid in self.graph['persons']:
                    person = self.graph['persons'][person_uid]
                    if person.is_click_in(event):
                        self.moving_object = person
                        break
            elif self.operation == 'create_relationship':
                for person_uid in self.graph['persons']:
                    person = self.graph['persons'][person_uid]
                    if person.is_click_in(event):
                        person.focus = not person.focus
                        if person.focus:
                            self.picked.append(person)
                        else:
                            if person in self.picked:
                                self.picked.remove(person)
                        break
                if len(self.picked) == 2:
                    relation = Relation(color='black', parent=self.picked[0], child=self.picked[1], name='')
                    self.add_relation(relation)
                    self.remove_all_focuses()
        self.paint_graph()

    def remove_all_focuses(self):
        self.picked = []
        for person_uid in self.graph['persons']:
            person = self.graph['persons'][person_uid]
            person.focus = False
            person.change()
        for relation_uid in self.graph['relations']:
            relation = self.graph['relations'][relation_uid]
            relation.focus = False
            relation.change()

    def end_move(self, event):
        self.moving_object = None

    def load_colors(self):
        self.colors = []
        if os.path.isfile(self.CONFIG_COLORS_FILE):
            with open(self.CONFIG_COLORS_FILE, 'r', encoding='utf8') as file:
                row = file.readline().strip()
                while row != '':
                    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', row)
                    if match:
                        self.colors.append(row)
                    row = file.readline().strip()

        if not self.colors:
            self.colors = self.COLORS_DEFAULT

    def set_operation(self, operation_name):
        if self.operation == operation_name:
            self.operation = None
            self.operations[operation_name].config(bg='white')
        elif self.operation is None:
            self.operation = operation_name
            self.operations[operation_name].config(bg='green')
        else:
            self.operations[self.operation].config(bg='white')
            self.operation = operation_name
            self.operations[operation_name].config(bg='green')


if __name__ == '__main__':
    m = Main()
    m.window.mainloop()
    # e = Exercise('Vianoce sú pred dverami a Bart a Lisa ukazujú rodičom ich list so želaniami.', 'Označ Barta a Lisu.', './Graphs/simpsons.json', ['960a90f3-cea5-41db-af45-ae88aaabf391', '6c90a9ee-1266-4faf-b7e7-30c42250f6e4'])
    # t = Test('Vianoce u Simpsonovcov')
    # t.exercises.append(e)
    # e = Exercise('Maggie taktiež niečo chce a preto sa snaží ukázať rodičom čo. Počúva ju ale iba mama.', 'Označ mamu Maggie.',
    #              './Graphs/simpsons.json', ['7d1dca26-d678-492d-ad22-08b8e20fed5d'])
    # t.exercises.append(e)
    # e = Exercise('Každý chlap v rodine Simsponovcov by chcel tetovanie.',
    #              'Kto sú chlapi v rodine?',
    #              './Graphs/simpsons.json', ['acf51105-c6d1-484f-8bf6-aa65cd6dbd42', '960a90f3-cea5-41db-af45-ae88aaabf391'])
    # t.exercises.append(e)
    # t.save('./tests/simpson.json')

