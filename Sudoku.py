from tkinter import *
from time import time

class Board:
    sets = []
    root = None
    rabbitHoleClock = 0
    backStep = 5

    class Box:
        avail = []
        set = 0
        spot = 0
        row = 0
        col = 0
        val = 0
        text = None

        def __init__(self, level):
            self.avail = []
            for _ in range(level):
                self.avail.append(True)

    def setup(self, level, root):
        self.sets = []
        self.root = root
        for widgets in root.winfo_children():
            widgets.destroy()
        root.destroy()
        root = Tk()
        for i in range(level):
            temp = []
            for j in range(level):
                box = self.Box(level)

                box.set = i
                box.spot = j
                box.row = (level // 3) * (i % 3) + j // 3
                box.col = 3*(i // 3) + j % 3

                temp.append(box)

                color = "white" if box.set % 2 else "light blue"
                box.text = Entry(root, bg=color, width=5, font=("Arial",25), justify="center")
                box.text.grid(row=box.row, column=box.col)

            self.sets.append(temp)

        switchVal = level + (3 if level==6 else -3)
        Button(root, text="solve", font=("Arial",20), command=self.solve).grid(row=10, column=level//3)
        Button(root, text="clear", font=("Arial",20), command=self.clear).grid(row=10,column=level//3 + 1 + level % 2)
        Button(root, text=(str(switchVal) + "?"), font=("Arial",20),
               command=lambda: self.setup(switchVal,root)).grid(row=10,column=level-1)

    def clear(self):
        for set in self.sets:
            for box in set:
                self.clean(box)
                box.text.delete(0,END)

    def found(self, box, val):
        if val == 0:
            self.clean(box)
            return True
        for i in range(len(box.avail)):
            box.avail[i] = False
        box.val = val
        for set in self.sets:
            for b in set:
                if b.row == box.row:
                    b.avail[val-1] = False
                if b.col == box.col:
                    b.avail[val-1] = False
                if b.set == box.set:
                    b.avail[val-1] = False
        for set in self.sets:
            for b in set:
                if not self.find(b):
                    return False
        return True

    def find(self, box):
        if box.val != 0:
            return True
        avail = len(self.sets[0])
        for poss in box.avail:
            if not poss:
                avail -= 1
        if avail == 1:
            return self.found(box, (box.avail.index(True) + 1))
        elif avail == 0:
            return False
        return True

    def clean(self, box):
        for a in range(len(box.avail)):
            box.avail[a] = True
        box.val = 0

    def retrieve(self):
        for set in self.sets:
            for box in set:
                self.clean(box)
        for set in self.sets:
            for box in set:
                try:
                    num = int(box.text.get()[0])
                    if not self.found(box, (num if num <= len(self.sets) else 0)):
                        return False
                except:
                    continue
        return True

    def display(self,check):
        bool = True
        for set in self.sets:
            for box in set:
                box.text.delete(0,END)
                if box.val == 0:
                    if check:
                        bool = False
                else:
                    box.text.insert(0,str(box.val))
                    self.root.update_idletasks()
        return bool

    def soloCheck(self, box):
        if box.val != 0:
            return True

        l = []
        for i in range(len(self.sets)):
            l.append(i+1)

        for b in self.sets[box.set]:
            if b.val == 0:
                if b == box:
                    continue
                c = 1
                for a in b.avail:
                    if a and c in l:
                        l.remove(c)
                    c+=1
            elif b.val in l:
                l.remove(b.val)
        if len(l) == 1:
            return self.found(box, l[0])
        return True

    def lineCheck(self, box):
        if box.val != 0:
            return True

        lr = []
        for i in range(len(self.sets)):
            lr.append(i+1)
        lc = lr[:]

        def notPres(b,l):
            if b.val == 0:
                c = 1
                for a in b.avail:
                    if a and c in l:
                        l.remove(c)
                    c+=1
            elif b.val in l:
                l.remove(b.val)

        for set in self.sets:
            for b in set:
                if b.set == box.set:
                    if b.val != 0:
                        try:
                            lr.remove(b.val)
                            lc.remove(b.val)
                        except:
                            continue
                elif b.row == box.row:
                    notPres(b,lr)
                elif b.col == box.col:
                    notPres(b,lc)

        for l in lr:
            for b in self.sets[box.set]:
                if b.row != box.row and b.val != 0:
                    b.avail[l-1] = False
        for l in lc:
            for b in self.sets[box.set]:
                if b.col != box.col and b.val != 0:
                    b.avail[l-1] = False

        return self.find(box)

    def pairCheck(self):

        def countTrue(l):
            c = 0
            for bool in l:
                if bool:
                    c += 1
            return c

        for set in self.sets:
            emptyBox = []
            for box in set:
                if box.val == 0:
                    emptyBox.append(box)
            if len(emptyBox) == 0:
                continue
            uselessVal = len(emptyBox)
            while len(emptyBox) > 0:
                check = emptyBox.pop(0)
                if countTrue(check.avail) == uselessVal:
                    continue

                l = []
                for i in range(len(self.sets)):
                    l.append(i+1)

                for a in range(len(check.avail)):
                    if check.avail[a]:
                       continue
                    l.remove(a+1)

                pairBox = [check]
                for box in emptyBox:
                    if box.avail == check.avail:
                        pairBox.append(box)

                if len(pairBox) == len(l):
                    for box in set:
                        if box.val != 0 or box in pairBox:
                            continue
                        for val in l:
                            box.avail[val-1] = False
        return True

    def solver(self, depth):
        if self.display(True):
            return True
        for set in self.sets:
            for box in set:
                if box.val == 0:
                    if self.soloCheck(box) and self.lineCheck(box) and self.pairCheck():
                        continue
                    else:
                        return False
        if self.display(True):
            return True

        return self.solverBox(depth)

    def solverBox(self, depth):

        def mycopy(self, oldList):
            newList = []
            for set in oldList:
                temp = []
                for b in set:
                    box = self.Box(len(oldList))

                    box.set = b.set
                    box.spot = b.spot
                    box.row = b.row
                    box.col = b.col
                    box.val = b.val
                    box.text = b.text
                    box.avail = b.avail[:]

                    temp.append(box)
                newList.append(temp)
            return newList

        setCpy = mycopy(self, self.sets)
        for set in setCpy:
            for box in set:
                if box.val != 0:
                    continue
                for a in range(len(box.avail)):
                    if box.avail[a]:
                        if self.found(self.sets[box.set][box.spot],a+1) and self.solver(depth+1):
                            return True
                        else:
                            self.sets = mycopy(self, setCpy)
                            if self.backStep >= 0 and time() - self.rabbitHoleClock > 2:
                                if depth > self.backStep:
                                    return False
                                else:
                                    self.rabbitHoleClock = time()
                                    self.backStep -= 1
                            elif self.backStep < 0:
                                self.clear()

        return False

    def solve(self):
        if not self.retrieve():
            return False
        self.rabbitHoleClock = time()
        self.solver(0)
        self.display(False)

    def __init__(self):
        root = Tk()

        Button(root, text="6?", width=15, font=("Arial",25), command=lambda: self.setup(6,root)).grid(row=0, column=0)
        Button(root, text="9?", width=15, font=("Arial",25), command=lambda: self.setup(9,root)).grid(row=0,column=1)

        root.mainloop()

Board()
