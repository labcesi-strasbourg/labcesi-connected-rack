# -*- coding: utf-8 -*-
import serial
from threading import Thread
from Tkinter import *
import time
import traceback

class RackEntry(LabelFrame):
    def __init__(self, label, row, column):
        LabelFrame.__init__(self, text=label)
        self.grid(row=row, column=column, sticky='nesw', ipadx=5, ipady=5, padx=5, pady=5)
        self.createWidgets()

    def createWidgets(self):
        self.quantity = IntVar()
        self.quantity.set(0)
        self.quantity.trace('w', self.on_value_change)
        self.quantity_label = Label(self, textvariable=self.quantity)
        self.quantity_label.grid(sticky='WE')

        self.unitary_cost = DoubleVar()
        self.unitary_cost.set(0)
        self.unitary_cost.trace('w', self.on_value_change)
        self.unitary_cost_entry = Entry(self, textvariable=self.unitary_cost)
        self.unitary_cost_entry.grid(sticky='WE')

        self.cost = DoubleVar()
        self.cost.set(0)
        self.cost_label = Label(self, textvariable=self.cost)
        self.cost_label.grid(sticky='WE')

        Label(self, text='boite(s)').grid(row=0, column=1)
        Label(self, text='€/boite').grid(row=1, column=1)
        Label(self, text='€').grid(row=2, column=1)

    def on_value_change(self, *args):
        try:
            self.cost.set(self.quantity.get() * self.unitary_cost.get())
        except Exception as e:
            print(e)

class Application(Frame):
    def __init__(self, master=None, racks_size=None):
        Frame.__init__(self, master)
        self._thread = None
        self.stop = False
        if racks_size:
            self.racks_size = racks_size
        else:
            self.racks_size = (1, 1)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        Label(self, text='Total cost:').grid(row=1, column=0)

        self.total_cost = DoubleVar()
        self.total_cost.set(0)
        self.total_cost_label = Label(self, textvariable=self.total_cost)
        self.total_cost_label.grid(row=1, column=1)

        Label(self, text='€').grid(row=1, column=3)

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit
        self.QUIT.grid(row=1, column=4) #, sticky='WE')

        self.racks = [[None] * self.racks_size[1] for i in xrange(self.racks_size[0])]
        self.racks_by_name = {}
        cur_name = ord('A') - 1
        for i in xrange(0, self.racks_size[0]):
            for j in xrange(0, self.racks_size[1]):
                cur_name += 1
                label = chr(cur_name)
                a_rack = RackEntry(label, 1+i, j)
                self.racks[i][j] = a_rack
                self.racks_by_name[label] = a_rack
                a_rack.cost.trace('w', self.on_one_rack_cost_change)

    def on_one_rack_cost_change(self, *args):
        total = sum(map(lambda a_row_of_racks: sum(map(lambda a_rack: a_rack.cost.get(), a_row_of_racks)), self.racks))
        self.total_cost.set(total)

    def listen_microbot(self):
        with serial.Serial('COM14', 115200, timeout=1) as ser:
            while not self.stop:
                line = ser.readline()   # read a '\n' terminated line
                if len(line) > 2:
                    print(line)
                    quantity = line[1:-1].strip()
                    try:
                        quantity = int(quantity)
                        self.racks_by_name[line[0]].quantity.set(quantity)
                    except Exception as e:
                        print("%s '%s'" % (e, quantity))
                        traceback.print_exc()
        self._thread = None

    def simulate(self):
        import random
        import time
        print("Simulating...")
        while not self.stop:
            i = random.randrange(self.racks_size[0])
            j = random.randrange(self.racks_size[1])
            delta = random.randint(-1,1)
            current = self.racks[i][j].quantity.get()
            new_value = max(current+delta, 0)
            print(i,j,delta, current, new_value)
            self.racks[i][j].quantity.set(new_value)
            time.sleep(2)
        self._thread = None

    def quit(self):
        while self._thread:
            self.stop = True
            time.sleep(0.5)
        Frame.quit(self)

    def mainloop(self):
        #self._thread = Thread(target=self.listen_microbot)
        self._thread = Thread(target=self.simulate)
        self._thread.start()
        Frame.mainloop(self)

root = Tk()
app = Application(master=root, racks_size=(2, 3))
root.protocol("WM_DELETE_WINDOW", app.quit)
app.mainloop()
root.destroy()
