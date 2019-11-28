class Item:
    def __init__(self, color):
        self.name = ''
        self.color = color
        self.focus = False
        self.focus_border_color = '#FF0000'

    def draw_item(self, canvas):
        pass

    def draw_info(self, canvas):
        pass


class Person(Item):
    def __init__(self, x, y, color):
        super().__init__(color)
        self.x = x
        self.y = y

    def move(self, event):
        pass

    def draw_item(self, canvas):
        pass

    def draw_info(self, canvas):
        super().draw_info(canvas)


class Relation(Item):
    def __init__(self, color, parent, child):
        super().__init__(color)
        self.parent = parent
        self.child = child

    def draw_info(self, canvas):
        super().draw_info(canvas)

    def draw_item(self, canvas):
        pass



