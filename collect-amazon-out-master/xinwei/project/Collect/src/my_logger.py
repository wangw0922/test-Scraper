import time
from tkinter import *


class Screen(object):

    def __init__(self):
        self.root = Tk()
        self.t = Text(self.root)
        self.t.pack()

    def ongo(self, word):
        self.t.insert(END, str(word) + "\n")
        time.sleep(0.1)
        self.t.update()

    def tk(self, word):
        self.ongo(word)
        self.root.mainloop()


s = Screen()
for i in range(1000):
    s.tk(f"{i}---李文霖")
