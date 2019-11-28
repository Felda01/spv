from tkinter import *
from tkinter import filedialog


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
        self.canvas_right = Canvas(self.frame, width=self.RIGHT_WIDTH, height=self.RIGHT_HEIGHT,bg='lightblue')
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
            self.infile = open(filename, "r")
            self.load(filename)

    def load(self,file_name):
        pass

    def save(self,file_name):
        pass

    def export(self):
        pass

    def delete_canvas(self):
        pass

    def click(self,event):
        pass

    def add_relation(self, what):
        pass

    def add_person(self):
        pass



if __name__ == '__main__':
    m = Main()
    m.window.mainloop()