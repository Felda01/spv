from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

class Cell:
    def __init__(self, emoji):
        self.emoji = emoji

    def operation(self):
        pass


class UpCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.move(dRow=-1)


class DownCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.move(dRow=-1)


class LeftCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.move(dRow=-1)


class RightCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.move(dRow=-1)


class FireCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.damage()


class HealCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        self.emoji.heal()

class EmptyCell(Cell):
    def __init__(self, emoji):
        super(emoji)

    def operation(self):
        pass


class Emoji:
    def __init__(self, life, stamina):
        self.x = 0
        self.y = 0
        self.life = life
        self.stamina = stamina

    def move(self, dRow=0, dCol=0):
        pass

    def damage(self):
        pass

    def heal(self):
        pass

class Main:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    TOP_WIDTH = WINDOW_WIDTH
    TOP_HEIGHT = 50
    BOTTOM_WIDTH = WINDOW_WIDTH
    BOTTOM_HEIGHT = WINDOW_HEIGHT - TOP_HEIGHT
    CELL_WIDTH = 64
    CELL_HEIGHT = 64

    def __init__(self):
        self.window = Tk()
        self.window.title('Cestovatel')
        self.window.resizable(False, False)
        self.frame = Frame(self.window,bg='black').pack()
        # TOP
        self.canvas_top = Canvas(self.frame, width=self.TOP_WIDTH, height=self.TOP_HEIGHT, bg='green')
        self.canvas_top.pack(side=TOP, expand=False)
        # Bottom
        self.canvas_bottom = Canvas(self.frame, width=self.BOTTOM_WIDTH, height=self.BOTTOM_HEIGHT, bg='tan')
        self.canvas_bottom.pack(side=BOTTOM, expand=False)
        # BUTTONS
        b = Button(self.canvas_top, text='Vyber mapu', command=self.select_file)
        b.place(x=10, y=10)

        self.map = [[1,2,3],[5,6]]
        self.paint()


    def start_game(self, filename):
        with open(filename, 'r') as file:
            for row in file:
                pass

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=".")
        if filename:
            self.infile = open(filename, "r")
            self.start_game(filename)
    
    def paint(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                self.canvas_bottom.create_rectangle(20+j*self.CELL_WIDTH,20+i*self.CELL_HEIGHT,20+(j+1)*self.CELL_WIDTH,20+(i+1)*self.CELL_HEIGHT)




if __name__ == "__main__":
    m = Main()
    m.window.mainloop()