import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import annotation as ant
from datetime import datetime


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_title("Построение графика")
        self.root.iconbitmap("src/spawnblack.ico")
        
        self.y_min = 30
        self.y_max = 80
        self.xrange = 15
        self.time_delta = 1
        self.current_time = 0
        self.x = np.arange(0, self.xrange, 1).tolist()
        # self.y = np.random.randint(0, 10, 1).tolist() + [0 for i in range(self.xrange - 1)]
        self.y = [self.y_min - 1 for i in range(self.xrange)]
        print(self.y)

        self.build_main_window()
        self.build_menubar()
        self.update_graph(False)

        ant.build_annotation(self.ax)
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', lambda event: ant._on_hover(event, self.line, 
                                                                                       self.fig, self.ax, 
                                                                                       self.x, self.y))
        
        tk.mainloop()

    def build_main_window(self):
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(11, 6)
        self.fig.tight_layout()
        self.ax.grid(True, alpha=0.4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)

        update_button = tk.Button(master=self.root, text="Обновить", 
                                  command=lambda: self.update_graph(False)).pack(side=tk.LEFT)
        update_button_cut = tk.Button(master=self.root, text="Обновить обрезать", 
                                  command=lambda: self.update_graph(True)).pack(side=tk.LEFT)
        #quit_button = tk.Button(master=self.root, text="Выход", command=self._quit).pack(side=tk.LEFT)

        self.canvas.draw()
    
    def build_menubar(self):
        """Function builds menubar"""

        menu_bar = tk.Frame(self.root, border=1, borderwidth=2)

        file_btn = MenubuttonBuilder(menu_bar, text="Файл")
        #file_btn.add_command(label="Обновить", command=lambda command: self.update_graph(False))
        #file_btn.add_command(label="Обновить обрезать", command=lambda command: self.update_graph(True))
        file_btn.add_command(label="Выход", command=self._quit)
        file_btn.pack(side=tk.LEFT, padx=2)

        help_btn = MenubuttonBuilder(menu_bar, text="Справка")
        help_btn.add_command(label="О программе", command=self.get_help)
        help_btn.pack(side=tk.LEFT, padx=2)

        menu_bar.pack(anchor="nw")

    def update_graph(self, is_cut_left, *args):
        #print(len(self.x), len(self.y))
        new_y_value = np.random.randint(self.y_min, self.y_max)
        self.current_time += self.time_delta

        if self.current_time <= self.xrange:
            #self.y[len(self.y) - self.y[::-1].index(0) - 1] = new_y_value
            self.y[self.y.index(self.y_min - 1)] = new_y_value
        else:
            self.x.append(self.x[-1] + 1)
            if is_cut_left:
                self.x.pop(0)
                self.y.pop(0)
            self.y.append(np.random.randint(self.y_min, self.y_max))

        self.ax.clear()
        
        self.line, = self.ax.plot(self.x, self.y, 
                                  color="#B198DA",
                                  marker=".", ms=12,
                                  picker=True, pickradius=5)
        ant.build_annotation(self.ax)

        self.ax.set_xticks(np.arange(self.x[0], self.x[-1] + 1, 0.5))
        self.ax.set_yticks(np.arange(20, 100, 5))
        self.ax.grid(True, alpha=0.3)
        self.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:g}'))
        
        self.canvas.draw()
    
    def get_help(self):
        dialogue = tk.Toplevel(self.root)
        dialogue.geometry("450x60")
        dialogue.resizable(False, False)
        self.label = tk.Label(dialogue, 
                              text=f"Простой калькулятор /// Асанов Даут Владимирович \n {str(datetime.today().date()).replace('-', '.')} /// GNU GPL 3.0")
        self.label.pack()
    
    def _quit(self):
        self.root.quit()
        self.root.destroy()


class MenubuttonBuilder:
    def __init__(self, parent, text):
        btn = tk.Menubutton(parent, text=text)
        btn.menu = tk.Menu(btn, tearoff=False)
        btn["menu"] = btn.menu
        
        self.btn = btn
    
    def get_btn(self):
        return self.btn
    
    def pack(self, **kwargs):
        self.btn.pack(**kwargs)
    
    def add_command(self, label, command):
        self.btn.menu.add_command(label=label, command=command)
        
if __name__ == "__main__":
    MainWindow()