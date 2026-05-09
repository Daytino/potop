import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
from PIL import Image, ImageTk
from pathlib import Path
import numpy as np
import annotation as ant
import configparser, os, platform
import cpuinfo, psutil


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self._read_config(config_path="src/mainwindowplot.cfg")
        if platform.uname().system == "Windows":
            self.root.iconbitmap("src/spawnblack.ico")

        self.current_time = 0
        self.root.wm_title(self.title)

        self.x = np.arange(0, self.x_range, 1).tolist()
        self.y = [self.y_min - 1 for i in range(self.x_range)]

        self.build_main_window()
        self.build_menubar()
        self.update_plot(is_cut_left=False)

        ant.build_annotation(self.plot)
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', lambda event: ant._on_hover(event, self.line_plot, 
                                                                                       self.fig, self.plot, 
                                                                                       self.x, self.y))
        tk.mainloop()

    def build_main_window(self):
        self.fig, self.plot = plt.subplots()
        self.fig.set_size_inches(11, 6)
        self.fig.tight_layout()
        self.plot.grid(True, alpha=0.4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)

        update_button = tk.Button(master=self.root, text="Обновить", 
                                  command=lambda: self.update_plot(False)).pack(side=tk.LEFT)
        update_button_cut = tk.Button(master=self.root, text="Обновить обрезать", 
                                  command=lambda: self.update_plot(True)).pack(side=tk.LEFT)
        #quit_button = tk.Button(master=self.root, text="Выход", command=self._quit).pack(side=tk.LEFT)

        self.canvas.draw()
    
    def build_menubar(self):
        menu_bar = tk.Frame(self.root, border=1, borderwidth=2)

        file_btn = MenubuttonBuilder(menu_bar, text="Файл")
        file_btn.add_command(label="Выход", command=self._quit)
        file_btn.pack(side=tk.LEFT, padx=2)

        help_btn = MenubuttonBuilder(menu_bar, text="Справка")
        help_btn.add_command(label="О программе", command=self.get_help)
        help_btn.pack(side=tk.LEFT, padx=2)

        menu_bar.pack(anchor="nw")

    def update_plot(self, is_cut_left):
        new_y_value = np.random.randint(self.y_min, self.y_max)

        self.current_time += self.time_delta
        if self.current_time <= self.x_range:
            self.y[self.y.index(self.y_min - 1)] = new_y_value
        else:
            self.x.append(self.x[-1] + 1)
            if is_cut_left:
                self.x.pop(0)
                self.y.pop(0)
            self.y.append(np.random.randint(self.y_min, self.y_max))

        self.plot.clear()
        
        self.line_plot, = self.plot.plot(self.x, self.y, 
                                  color="#B198DA",
                                  marker=".", ms=12,
                                  picker=True, pickradius=5)
        
        self.update_plot_environment()
        self.canvas.draw()
    
    def update_plot_environment(self):
        ant.build_annotation(self.plot)
        self.plot.set_xticks(np.arange(self.x[0], self.x[-1] + 1, 0.5))
        self.plot.set_yticks(np.arange(self.y_min, self.y_max, 5))
        self.plot.grid(True, alpha=0.4)
        self.plot.xaxis.set_major_formatter(StrMethodFormatter('{x:g}'))

    def get_help(self):
        dialogue = tk.Toplevel(self.root)
        dialogue.geometry("380x200")
        dialogue.resizable(False, False)
        dialogue.title("О программе")
        dialogue.transient(self.root)
        dialogue.grab_set()
        dialogue.update_idletasks()
        
        x = self.root.winfo_x() + (self.root.winfo_width() - dialogue.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialogue.winfo_height()) // 2
        dialogue.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialogue)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        try:
            logo_image = Image.open(os.path.join(images_path, "potop.jpg")).resize((120, 120))
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(main_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        except:
            logo_label = tk.Label(main_frame, text="⚙️", font=("Arial", 24))
            logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        
        info_text = f"{self.title}  ({version})\nАсанов Даут Владимирович\nGNU GPL 3.0"
        info_label = tk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=0, column=1, sticky=tk.W)
        
        github_frame = tk.Frame(main_frame)
        github_frame.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        try:
            github_img = Image.open(os.path.join(images_path, "github_icon.png")).resize((16, 16))
            github_photo = ImageTk.PhotoImage(github_img)
            github_icon = tk.Label(github_frame, image=github_photo)
            github_icon.image = github_photo
            github_icon.pack(side=tk.LEFT)
        except:
            github_icon = tk.Label(github_frame, text="🔗", font=("Consolas", 10))
            github_icon.pack(side=tk.LEFT)
        
        github_link = tk.Label(github_frame, 
                            text="GitHub репозиторий", 
                            fg="#0366d6", 
                            cursor="hand2", 
                            font=("Consolas", 9, "underline"))
        github_link.pack(side=tk.LEFT, padx=(3, 0))
    
        def _open_github(event=None):
            import webbrowser
            webbrowser.open(repository)
            del webbrowser

        github_link.bind("<Button-1>", _open_github)
        
        def _on_enter(event):
            github_link.config(fg="#0056b3")
        
        def _on_leave(event):
            github_link.config(fg="#0366d6")
        
        github_link.bind("<Enter>", _on_enter)
        github_link.bind("<Leave>", _on_leave)
        
        close_btn = tk.Button(dialogue, text="OK", command=dialogue.destroy, width=10)
        close_btn.pack(pady=(8, 0))
            
    def _read_config(self, config_path):
        global version, repository, images_path
        config = configparser.ConfigParser()
        config.read(config_path)

        self.title = config.get("General", "app_name")
        version = config.get("General", "version")
        repository = config.get("General", "repository")

        images_path = config.get("Paths", "images_path")

        self.y_min = config.getint("Plotticks", "y_min")
        self.y_max = config.getint("Plotticks", "y_max")
        self.x_range = config.getint("Plotticks", "x_range")

        self.time_delta = config.getint("Time", "time_delta")

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


class CPUWindow(MainWindow):
    def __init__(self):
        super().__init__()
    
    def update_plot(self, is_cut_left):
        new_y_value = psutil.cpu_percent()

        self.current_time += self.time_delta
        if self.current_time <= self.x_range:
            self.y[self.y.index(self.y_min - 1)] = new_y_value
        else:
            self.x.append(self.x[-1] + 1)
            if is_cut_left:
                self.x.pop(0)
                self.y.pop(0)
            self.y.append(np.random.randint(self.y_min, self.y_max))

        self.plot.clear()
        
        self.line_plot, = self.plot.plot(self.x, self.y, 
                                  color="#B198DA",
                                  marker=".", ms=12,
                                  picker=True, pickradius=5)
        
        self.update_plot_environment()
        self.canvas.draw()

if __name__ == "__main__":
    CPUWindow()