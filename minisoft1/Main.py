from tkinter import *
import glob

class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class Rule:
    def __init__(self, line):
        array = line.strip().split(' -> ')
        if len(array[0] > 1):
            raise ValueError
        self.search = array[0]
        self.replace = array[1].split(',')
        
class Character:
    def __init__(self,file_name,name):
        self.char_name = name
        self.image = PhotoImage(file=file_name)

class Main:
    def __init__(self, file_name='config.txt'):
        self.canvas = Canvas(width=1000,height=600)
        self.canvas.pack()
        self.characters = dict()
        self.burger = [PhotoImage(file='./images/borger_top.png'),PhotoImage('./images/burger_bottom.png')]
        self.root = None
        with open('config.txt','r') as file:
            row = file.readline().strip()
            for i in glob.glob(row+'/*.png'):
                absolute_path = i.replace('\\','/')
                file_name = absolute_path.split('/')[-1]
                char = file_name.split('.')[0]
                self.characters[char] = Character(absolute_path,char)
                self.canvas.create_image(100, 100, image=self.characters[char].image)
                
    def init_word(self,word):
        pass

if __name__ == '__main__':
    main = Main()
    main.canvas.mainloop()
