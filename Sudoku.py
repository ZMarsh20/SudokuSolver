from tkinter import *

class Board:
    sets = []
    level = 0
    root = None

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
            for _ in range(level): self.avail.append(True)

    def setup(self, level, root):
        self.sets = []
        self.root = root
        self.level = level
        for widgets in root.winfo_children(): widgets.destroy()
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
        if not box.avail[val] and box.val != val+1: return False
        box.avail = [False for _ in range(self.level)]
        box.val = val+1
        for set in self.sets:
            for b in set:
                if b.row == box.row: b.avail[val] = False
                if b.col == box.col: b.avail[val] = False
                if b.set == box.set: b.avail[val] = False
        for set in self.sets:
            for b in set:
                if not self.find(b): return False
        return True

    def find(self, box):
        if box.val == 0:
            avail = sum(box.avail)
            if avail == 1: return self.found(box, (box.avail.index(True)))
            elif avail == 0: return False
        return True

    def clean(self, box):
        for a in range(self.level): box.avail[a] = True
        box.val = 0

    def retrieve(self):
        for set in self.sets:
            for box in set:
                self.clean(box)
        for set in self.sets:
            for box in set:
                try:
                    num = int(box.text.get()[0])
                    if not self.found(box, (num-1 if num <= self.level else 0)): return False
                except: continue
        return True

    def display(self,check=False):
        bool = True
        for set in self.sets:
            for box in set:

                # # better looking code but looks worse on the board
                # if check and box.val == 0:
                #     return False
                # else:
                #     box.text.delete(0,END)
                #     if box.val != 0:
                #         box.text.insert(0,str(box.val))
                #         self.root.update_idletasks()

                box.text.delete(0,END)
                if box.val == 0:
                    if check: bool = False
                else:
                    box.text.insert(0,str(box.val))
                    self.root.update_idletasks()
        return bool

    def soloCheck(self, box):
        if box.val == 0:
            lists = []
            boxSet = set([x for (x, avail) in zip((x for x in range(self.level)), box.avail) if avail])
            for b in self.sets[box.set]:
                if b.val == 0 and b != box:
                    lists.append([x for (x, avail) in zip((x for x in range(self.level)), b.avail) if avail])
            if lists:
                l = list(boxSet.difference(set.union(*[set(avail) for avail in lists])))
                if len(l) == 1: return self.found(box, l[0])
        return True

    def lineCheck(self, box):
        if box.val == 0:
            listr = []
            listc = []
            boxVals = []
            for s in self.sets:
                for b in s:
                    if b.set != box.set and box.val != 0: boxVals.append(box.val-1)
                    elif box.val == 0:
                        if b.row == box.row: listr.append([x for (x, avail) in zip((x for x in range(self.level)), b.avail) if not avail])
                        elif b.col == box.col: listc.append([x for (x, avail) in zip((x for x in range(self.level)), b.avail) if not avail])


            if listr:
                lr = list(set.intersection(*[set(l) for l in listr],set(boxVals)))
                for l in lr:
                    for b in self.sets[box.set]:
                        if b.row != box.row and b.val == 0:
                            b.avail[l] = False
            if listc:
                lc = list(set.intersection(*[set(l) for l in listc],set(boxVals)))
                for l in lc:
                    for b in self.sets[box.set]:
                        if b.col != box.col and b.val == 0:
                            b.avail[l] = False
        return True

    def pairCheck(self):
        for set in self.sets:
            emptyBox = list(filter(lambda box: box.val == 0, set))
            if len(emptyBox) != 0:
                uselessVal = len(emptyBox)
                while len(emptyBox) > 0:
                    check = emptyBox.pop(0)
                    if sum(check.avail) != uselessVal:
                        l = [x for (x, avail) in zip((x for x in range(self.level)), check.avail) if avail]

                        pairBox = list(filter(lambda box: box.avail == check.avail, emptyBox))
                        for box in pairBox: emptyBox.remove(box)
                        pairBox.append(check)

                        if len(pairBox) == len(l):
                            for box in set:
                                if box.val == 0 and box not in pairBox:
                                    for val in l:
                                        box.avail[val] = False
        return True

    def solver(self, depth=0):
        for set in self.sets:
            for box in set:
                if box.val == 0:
                    if not (self.lineCheck(box) and self.pairCheck() and self.soloCheck(box)): return False
                    if not self.find(box): return False
        if self.display(True): return True
        return self.solverBox(depth)

    def solverBox(self, depth):

        def mycopy(self, oldList):                  # needed my own deepcopy() because of tkinter shtuff
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
                if box.val == 0:
                    for a in range(self.level):
                        if box.avail[a]:
                            if self.found(self.sets[box.set][box.spot],a) and self.solver(depth+1): return True
                            self.sets = mycopy(self, setCpy)
                            if depth > 3: return False

    def solve(self):
        if self.retrieve():
            self.solver()
            self.display()

    def __init__(self):
        root = Tk()

        Button(root, text="6?", width=15, font=("Arial",25), command=lambda: self.setup(6,root)).grid(row=0, column=0)
        Button(root, text="9?", width=15, font=("Arial",25), command=lambda: self.setup(9,root)).grid(row=0,column=1)

        root.mainloop()

Board()
