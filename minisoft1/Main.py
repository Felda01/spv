from tkinter import *
import glob
import sys
from PIL import Image
from PIL import ImageTk

class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class Rule:
    def __init__(self, line):
        self.name = line.strip()
        array = self.name.split(' -> ')
        if len(array) != 2:
            raise ValueError
        self.search = array[0].split(',')
        self.replace = array[1].split(',')
        self.replace_characters = []
        self.search_characters = []
        self.height = max(len(self.search),len(self.replace))*Character.HEIGHT
        self.image = None

    def set_charatcters(self,characters):
        for i in self.search:
            self.search_characters.append(characters[i])
        for i in self.replace:
            self.replace_characters.append(characters[i])
        self.combine_images()

    def combine_images(self):
        image1 = map(Image.open, ['./images/processed/'+i.char_name+'.png' for i in self.search_characters])
        image2 = map(Image.open, ['./images/processed/'+i.char_name+'.png' for i in self.replace_characters])
        new_image = Image.new('RGBA',(Character.WIDTH*2+Character.ARROW, self.height),'white')

        y_offset = (self.height - len(self.search_characters)*Character.HEIGHT)//2
        for im in image1:
            new_image.paste(im, (0,y_offset))
            y_offset += Character.HEIGHT

        new_image.paste(Image.open('./images/arrow.png'), (Character.WIDTH, (self.height-Character.ARROW)//2))

        y_offset = (self.height - len(self.replace_characters)*Character.HEIGHT)//2
        for im in image2:
            new_image.paste(im, (Character.WIDTH+Character.ARROW,y_offset))
            y_offset += Character.HEIGHT
        file_name = self.name.replace(',','_').replace(' -> ','A')
        print(new_image)
        new_image.save('./images/rules/'+file_name+'.png',"PNG")

        self.image = PhotoImage(file='./images/rules/'+file_name+'.png')

        
class Character:
    HEIGHT = 50
    WIDTH = 170
    ARROW = 32
    def __init__(self,file_name,name):
        self.char_name = name
        self.file_name = file_name
        image = Image.open(file_name)
        image = image.resize((self.WIDTH,self.HEIGHT), Image.ANTIALIAS)
        image.save('./images/processed/'+self.char_name+'.png','PNG')
        self.image = PhotoImage('./images/processed/'+self.char_name+'.png')

class Main:
    def __init__(self, file_name='config.txt'):
        self.canvas = Canvas(width=1000,height=600,bg='#bada55')
        self.canvas.pack()
        self.characters = dict()
        self.rules = dict()
        self.burger = [PhotoImage(file='./images/burger_top.png'),PhotoImage('./images/burger_bottom.png')]
        self.root = None
        with open(file_name,'r') as file:
            row = file.readline().strip()

            for i in glob.glob(row+'/*.png'):
                absolute_path = i.replace('\\','/')
                file_name = absolute_path.split('/')[-1]
                char = file_name.split('.')[0]
                self.characters[char] = Character(absolute_path,char)

            row = file.readline().strip()
            while row != '':
                rule = Rule(row)
                rule.set_charatcters(self.characters)
                self.rules[row] = rule
                row = file.readline().strip()
            print(self.rules)

        self.init_piant()

    def init_piant(self):
        self.button_rules = []
        x = 0
        y = 0
        for key in self.rules:
            rule = self.rules[key]
            self.button_rules.append(Button(master=self.canvas,command= lambda: self.apply_rule(key),image=rule.image))
            self.button_rules[-1].place(x=x,y=y)
            y += rule.height+10
            pass

    def init_word(self,word):
        pass

    def apply_rule(self, key):
        pass

if __name__ == '__main__':
    main = Main()
    main.canvas.mainloop()
