import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
from PIL import Image, ImageTk
from abc import abstractmethod
import annotation as ant
import configparser, os, platform, time
import cpuinfo, psutil


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self._read_config(config_path="src/mainwindowplot.cfg")
        if platform.uname().system == "Windows":
            self.root.iconbitmap("src/spawnblack.ico")

        self.current_time = 0
        self._set_window_title(self.title)

        self.x = np.arange(0, self.x_range, self.time_delta).tolist()
        self.y = [self.y_min for i in range(len(self.x))]

        self.build_main_window()
        self.build_menubar()
        self.update_plot(is_cut_left=False)

        ant.build_annotation(self.plot)
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', lambda event: ant._on_hover(event, self.line_plot, 
                                                                                       self.fig, self.plot, 
                                                                                       self.x, self.y))
        self._cycle()
        tk.mainloop()

    def build_main_window(self):
        self.fig, self.plot = plt.subplots()
        self.fig.set_size_inches(11, 7)
        self.fig.tight_layout()
        self.plot.grid(True, alpha=0.4)
        self.plot.set_facecolor('#f0f0f0')
        self.fig.set_facecolor('#f0f0f0')
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)

        # update_button = tk.Button(master=self.root, text="Обновить", 
        #                           command=lambda: self.update_plot(False)).pack(side=tk.LEFT)
        # update_button_cut = tk.Button(master=self.root, text="Обновить обрезать", 
        #                           command=lambda: self.update_plot(True)).pack(side=tk.LEFT)
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

    def update_plot(self, is_cut_left, new_y_value=0):
        if new_y_value != 0:
            self.current_time += self.time_delta
        if self.current_time <= self.x_range:
            self.y[self.y.index(self.y_min)] = new_y_value
        else:
            self.x.append(self.x[-1] + self.time_delta)
            
            if is_cut_left:
                self.x.pop(0)
                self.y.pop(0)
            self.y.append(new_y_value)

        self.plot.clear()
        
        self.line_plot, = self.plot.plot(self.x, self.y, 
                                  color="#313131",
                                  marker=".", ms=12,
                                  picker=True, pickradius=5)
        
        self.update_plot_environment(self.y_min, self.y_max, 5)
        self.canvas.draw()
    
    def update_plot_environment(self, y_min, y_max, y_delta):
        ant.build_annotation(self.plot)
        self.plot.set_xticks(np.arange(self.x[0], self.x[-1] + 1, self.time_delta))
        self.plot.set_yticks(np.arange(y_min, y_max, y_delta))
        self.plot.grid(True, alpha=0.4)
        self.plot.xaxis.set_major_formatter(StrMethodFormatter('{x:g}'))

    def get_help(self):
        dialogue = tk.Toplevel(self.root)
        dialogue.geometry("380x180")
        dialogue.resizable(False, False)
        dialogue.title("О программе")
        dialogue.transient(self.root)
        dialogue.grab_set()
        dialogue.update_idletasks()
        if platform.uname().system == "Windows":
            dialogue.iconbitmap("src/spawnblack.ico")
        
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
        except Exception as e:
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
        close_btn.pack(pady=(0, 8))
            
    def _read_config(self, config_path):
        global version, repository, images_path
        config = configparser.ConfigParser()
        config.read(config_path)
        
        self.title = config.get("General", "app_name")
        version = config.get("General", "version")
        repository = config.get("General", "repository")

        images_path = config.get("Paths", "images_path")

        if not hasattr(self, 'y_min'): self.y_min = config.getint("Plotticks", "y_min")
        if not hasattr(self, 'y_max'): self.y_max = config.getint("Plotticks", "y_max")
        self.x_range = config.getint("Plotticks", "x_range")

        self.time_delta = config.getfloat("Time", "time_delta")
    
    def _set_window_title(self, window_title):
        if window_title:
            self.root.wm_title(window_title)
        else:
            self.title = "potop"
            self.root.wm_title(self.title)
    
    @abstractmethod
    def _cycle(self):
        pass

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
        self.title = "Температура CPU"
        self.start_time = time.time()
        self.y_min = 0
        self.y_max = 50
        super().__init__()
    
    def build_main_window(self):
        super().build_main_window()

        cpu_info = cpuinfo.get_cpu_info()
        cpu_model = cpu_info["brand_raw"]
        cpu_arch = cpu_info["arch"]
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        
        self.canvas.get_tk_widget().pack_forget()
        
        self.info_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=1)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(self.info_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        info_frame_size = 12
        info_frame_family = "Consolas"
        model_label = tk.Label(left_frame, text=f"Процессор: {cpu_model}", 
                              font=(info_frame_family, info_frame_size, "bold"), anchor=tk.W)
        model_label.pack(anchor=tk.W)
        
        arch_label = tk.Label(left_frame, text=f"Архитектура: {cpu_arch}", 
                             font=(info_frame_family, info_frame_size), anchor=tk.W)
        arch_label.pack(anchor=tk.W)
        
        cores_label = tk.Label(left_frame, 
                              text=f"Ядра: {cpu_cores} | Потоки: {cpu_threads}", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        cores_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.uptime_label = tk.Label(right_frame, text="Время работы: --", 
                                 font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.uptime_label.pack(anchor=tk.W)

        self.freq_label = tk.Label(right_frame, text="Частота: -- MHz", 
                                   font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.freq_label.pack(anchor=tk.E)
        
        self.percent_label = tk.Label(right_frame, text="Загрузка: --%", 
                                      font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.percent_label.pack(anchor=tk.E)
    
    def update_plot_environment(self, y_min, y_max, y_delta):
        self.plot.set_xlabel("Время (с)", fontfamily='Consolas', fontsize=12)
        self.plot.set_ylabel("Загрузка (%)", fontfamily='Consolas', fontsize=12)
        self.plot.set_title("Загрузка процессора", fontfamily='Consolas', fontsize=12, fontweight='bold')
        return super().update_plot_environment(self.y_min, self.y_max, 2.5)

    def _cycle(self):
        cpu_percent = psutil.cpu_percent()
        super().update_plot(is_cut_left=True, new_y_value=cpu_percent)
        cpu_freq = psutil.cpu_freq().current
        self.freq_label.config(text=f"Частота: {cpu_freq:.0f} MHz")

        self.percent_label.config(text=f"Загрузка: {cpu_percent}%")
        
        elapsed = self.current_time - 2
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        days = int(elapsed // 86400)
        if days > 0:
            self.uptime_label.config(text=f"Время работы: {days}д {elapsed_str}")
        else:
            self.uptime_label.config(text=f"Время работы: {elapsed_str}")
        self.root.after(int(self.time_delta * 1000), self._cycle)


class RAMWindow(MainWindow):
    def __init__(self):
        self.title = "Использование RAM"
        self.start_time = time.time()
        self.y_min = 0
        self.y_max = 100
        super().__init__()
    
    def build_main_window(self):
        super().build_main_window()
        
        ram_info = psutil.virtual_memory()
        ram_total = ram_info.total / 1024**3
        
        self.canvas.get_tk_widget().pack_forget()
        
        self.info_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=1)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(self.info_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)

        info_frame_size = 12
        info_frame_family = "Consolas"
        self.total_label = tk.Label(left_frame, text=f"Всего RAM: {ram_total:.1f} GB", 
                                font=(info_frame_family, info_frame_size, "bold"), anchor=tk.W)
        self.total_label.pack(anchor=tk.W)

        self.avail_label = tk.Label(left_frame, text="Доступно: -- GB", 
                                font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.avail_label.pack(anchor=tk.W)

        self.used_label = tk.Label(left_frame, text="Используется: -- GB", 
                                font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.used_label.pack(anchor=tk.W)

        self.free_label = tk.Label(left_frame, text="Свободно: -- GB", 
                                font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.free_label.pack(anchor=tk.W)

        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.uptime_label = tk.Label(right_frame, text="Время работы: --", 
                                    font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.uptime_label.pack(anchor=tk.E)

        self.percent_label = tk.Label(right_frame, text="Использование: --%", 
                                    font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.percent_label.pack(anchor=tk.E)
    
    def update_plot_environment(self, y_min, y_max, y_delta):
        self.plot.set_xlabel("Время (с)", fontfamily='Consolas', fontsize=12)
        self.plot.set_ylabel("Использование (%)", fontfamily='Consolas', fontsize=12)
        self.plot.set_title("Использование RAM", fontfamily='Consolas', fontsize=12, fontweight='bold')
        return super().update_plot_environment(self.y_min, self.y_max, 5)

    def _cycle(self):
        ram_info = psutil.virtual_memory()
        ram_percent = ram_info.percent
        ram_free = ram_info.free / 1024 ** 3
        ram_avail = ram_info.available / 1024 ** 3
        ram_used = ram_info.used / 1024 ** 3
        
        super().update_plot(is_cut_left=True, new_y_value=ram_percent)
        
        self.avail_label.config(text=f"Доступно: {ram_avail:.1f} GB")
        self.used_label.config(text=f"Использовано: {ram_used:.1f} GB")
        self.percent_label.config(text=f"Использование: {ram_percent}%")
        self.free_label.config(text=f"Свободно: {ram_free:.1f} GB")
        
        elapsed = time.time() - self.start_time
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        days = int(elapsed // 86400)
        if days > 0:
            self.uptime_label.config(text=f"Время работы: {days}д {elapsed_str}")
        else:
            self.uptime_label.config(text=f"Время работы: {elapsed_str}")
        
        self.root.after(int(self.time_delta * 1000), self._cycle)
    
if __name__ == "__main__":
    RAMWindow()