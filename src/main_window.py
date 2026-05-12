import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
from PIL import Image, ImageTk
from abc import abstractmethod
from typing import Union
from window_switcher import WindowSwitcher
from database_saver import ReportSaver
import annotation as ant
import configparser, os, platform, datetime, time

switcher = WindowSwitcher()

class MainWindow:
    def __init__(self, window_type: str="Main") -> None:
        self.window_type = window_type
        self.root = tk.Tk()
        self._after_id = None
        self.is_running = True

        self.db = ReportSaver()
        self.last_peak_saved = 0
        
        self._read_config(config_path="src/potop.cfg")
        if platform.uname().system == "Windows":
            try:
                self.root.iconbitmap("src/spawnblack.ico")
            except:
                pass

        self.current_time = 0
        self._set_window_title(self.title)

        self.x = np.arange(0, self.x_range, self.time_delta).tolist()
        self.y = [self.y_min for _ in range(len(self.x))]

        if not hasattr(self, 'y_sent'):
            self.y_sent = [self.y_min for _ in range(len(self.x))]

        self.build_main_window()
        self.build_menubar()
        self.update_plot(is_cut_left=False)

        ant.build_annotation(self.plot)
        self.cid = self.fig.canvas.mpl_connect(
            'motion_notify_event',
            lambda event: ant._on_hover(
                event, self.line_plot, self.fig, self.plot,
                self.x, self.y, x_unit=self.x_unit, y_unit=self.y_unit
            )
        )
    
        switcher.register(window_type, self)
        
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        
        self._cycle()

    def build_main_window(self) -> None:
        self.fig, self.plot = plt.subplots()
        self.fig.set_size_inches(11, 7)
        self.fig.tight_layout()
        self.plot.grid(True, alpha=0.4)
        self.plot.set_facecolor('#f0f0f0')
        self.fig.set_facecolor('#f0f0f0')
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def build_menubar(self) -> None:
        menu_bar = tk.Frame(self.root, border=1, borderwidth=2)

        file_btn = MenubuttonBuilder(menu_bar, text="Файл")
        file_btn.add_command(label="Сохранить отчёт как...",
                             command=self.save_report_as)
        file_btn.add_separator()
        file_btn.add_command(label="Процессор", 
                           command=lambda: switcher.switch_to("CPU"))
        file_btn.add_command(label="Оперативная память", 
                           command=lambda: switcher.switch_to("RAM"))
        file_btn.add_command(label="Сеть", 
                           command=lambda: switcher.switch_to("Net"))
        file_btn.add_command(label="Диск", 
                           command=lambda: switcher.switch_to("Disk"))
        file_btn.add_separator()
        file_btn.add_command(label="Настройки", command=self.open_settings)
        file_btn.add_command(label="Выход", command=self._quit_all)
        file_btn.pack(side=tk.LEFT, padx=2, pady=1)

        help_btn = MenubuttonBuilder(menu_bar, text="Справка")
        help_btn.add_command(label="О программе", command=self.get_help)
        help_btn.pack(side=tk.LEFT, padx=2)

        menu_bar.pack(anchor="nw", fill=tk.X)

    def update_plot(self, is_cut_left: bool, 
                    new_y_value: Union[float, int] = 0, 
                    new_y_value_sent: Union[float, int] = 0) -> None:
        self.current_time += self.time_delta
        if self.current_time <= self.x_range + 1:
            self.y[self.y.index(self.y_min)] = new_y_value
            if hasattr(self, 'y_sent'):
                self.y_sent[self.y_sent.index(self.y_min)] = new_y_value_sent
        else:
            self.x.append(self.x[-1] + self.time_delta)
            self.y.append(new_y_value)
            if hasattr(self, 'y_sent'):
                self.y_sent.append(new_y_value_sent)
            if is_cut_left:
                self.x.pop(0)
                self.y.pop(0)
                if hasattr(self, 'y_sent'):
                    self.y_sent.pop(0)

        self.plot.clear()
        
        self.line_plot, = self.plot.plot(self.x, self.y,
                                color="#313131",
                                marker=".", ms=12,
                                picker=True, pickradius=5)
        
        if hasattr(self, 'y_sent') and self.window_type == "Net":
            self.line_plot_sent, = self.plot.plot(self.x, self.y_sent,
                                    color="#689d6a",
                                    marker=".", ms=8,
                                    label="Upload",
                                    picker=True, pickradius=5)
        
        self.update_plot_environment(self.y_min, self.y_max, self.y_delta)
        self.canvas.draw()
    
    def update_plot_environment(self, y_min: int, 
                                y_max: int, 
                                y_delta: Union[float, int]) -> None:
        ant.build_annotation(self.plot)
        self.plot.set_xticks(np.arange(self.x[0], self.x[-1] + 1, self.time_delta))
        self.plot.set_yticks(np.arange(y_min, y_max, y_delta))
        self.plot.grid(True, alpha=0.4)
        self.plot.xaxis.set_major_formatter(StrMethodFormatter('{x:g}'))

    def get_help(self) -> None:
        dialogue = tk.Toplevel(self.root)
        dialogue.geometry("380x180")
        dialogue.resizable(False, False)
        dialogue.title("О программе")
        dialogue.transient(self.root)
        dialogue.grab_set()
        dialogue.update_idletasks()
        if platform.uname().system == "Windows":
            try:
                dialogue.iconbitmap("src/spawnblack.ico")
            except:
                pass
        
        x = self.root.winfo_x() + (self.root.winfo_width() - dialogue.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialogue.winfo_height()) // 2
        dialogue.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialogue)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 5))
        
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
        github_frame.grid(row=1, column=1, sticky=tk.W, pady=(5, 2))
        
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

        github_link.bind("<Button-1>", _open_github)
        
        def _on_enter(e): github_link.config(fg="#0056b3")
        def _on_leave(e): github_link.config(fg="#0366d6")
        github_link.bind("<Enter>", _on_enter)
        github_link.bind("<Leave>", _on_leave)
        
        close_btn = tk.Button(dialogue, text="OK", command=dialogue.destroy, width=10)
        close_btn.pack(pady=(0, 8))
    
    def save_report_as(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        valid_y = [v for v in self.y if v != self.y_min]
        avg_value = sum(valid_y) / len(valid_y) if valid_y else 0
        
        report = f"""Отчёт о нагрузке: {self.title}
    Дата: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
    Длительность: {self.current_time:.0f} с

    Среднее значение: {avg_value:.2f}{self.y_unit}
    Максимальное значение: {getattr(self, 'y_max_value', 0):.2f}{self.y_unit}
    Время максимума: {getattr(self, 'max_time_full', 'N/A')}
    Пиковое время: {getattr(self, 'max_time', 0):.0f} с

    Данные графика:
    {list(zip(self.x, self.y))}
    """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        data_str = str(list(zip(self.x, self.y)))
        self.db.save_report(self.window_type, avg_value, 
                        getattr(self, 'y_max_value', 0),
                        getattr(self, 'max_time_full', ''), data_str)

    def open_settings(self):
        dialogue = tk.Toplevel(self.root)
        dialogue.geometry("420x160")
        dialogue.resizable(False, False)
        dialogue.title("Настройки")
        dialogue.transient(self.root)
        dialogue.grab_set()
        dialogue.update_idletasks()

        if platform.uname().system == "Windows":
            try:
                dialogue.iconbitmap("src/spawnblack.ico")
            except:
                pass
        
        x = self.root.winfo_x() + (self.root.winfo_width() - dialogue.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialogue.winfo_height()) // 2
        dialogue.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialogue)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        config_path = os.path.abspath("src/potop.cfg")
        
        info_label = tk.Label(main_frame, 
                            text="Окно настроек в разработке.\nДля настройки редактируйте файл:",
                            font=("Consolas", 10), justify=tk.LEFT)
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        path_entry = tk.Entry(main_frame, font=("Consolas", 10), 
                            fg="#0366d6", readonlybackground="white",
                            justify=tk.LEFT, relief=tk.FLAT, background="#f0f0f0", bg="#f0f0f0")
        path_entry.insert(0, config_path)
        path_entry.config(state="readonly")
        path_entry.pack(fill=tk.X, pady=(0, 10))
        
        close_btn = tk.Button(dialogue, text="OK", command=dialogue.destroy, width=10)
        close_btn.pack(pady=(0, 5))

    def _read_config(self, 
                     config_path: str) -> None:
        global version, repository, images_path
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path)
        
        self.title = config.get("General", "app_name")
        version = config.get("General", "version")
        repository = config.get("General", "repository")
        images_path = config.get("Paths", "images_path")

        section = f"Window.{self.window_type}"
        if not config.has_section(section):
            section = "Window.Main"
        
        self.y_min = config.getint(section, "y_min")
        self.y_max = config.getint(section, "y_max")
        self.y_delta = config.getfloat(section, "y_delta")
        self.x_range = config.getint(section, "x_range")
        self.x_unit = config.get(section, "x_unit")
        self.y_unit = config.get(section, "y_unit")
        self.time_delta = config.getfloat("Time", "time_delta")
    
    def _set_window_title(self, 
                          window_title: str) -> None:
        if window_title:
            self.root.wm_title(window_title)
        else:
            self.title = "potop"
            self.root.wm_title(self.title)
    
    @abstractmethod
    def _cycle(self):
        pass

    def _update_runtime_label(self, 
                              start_time: int):
        elapsed = time.time() - start_time
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        days = int(elapsed // 86400)
        if days > 0:
            self.uptime_label.config(text=f"Время работы: {days}d {elapsed_str}")
        else:
            self.uptime_label.config(text=f"Время работы: {elapsed_str}")

    def _cleanup(self) -> None:
        self.is_running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _on_close(self) -> None:
        self._quit_all()

    def _quit_all(self) -> None:
        switcher.quit_all()
        self.root.quit()

    def __str__(self):
        return f"MainWindow({self.window_type})"


class MenubuttonBuilder:
    def __init__(self, parent: tk.Frame, 
                 text: str, 
                 is_menu_right: bool = False,
                 **kwargs) -> None:
        btn = tk.Menubutton(parent, 
                            text=text,
                            **kwargs)
        btn.menu = tk.Menu(btn, tearoff=False)
        btn["menu"] = btn.menu
        self.btn = btn

        if is_menu_right:
            btn.bind("<Button-1>", self._show_menu_right)
        
    def pack(self, 
             **kwargs) -> None:
        self.btn.pack(**kwargs)

    def _show_menu_right(self, 
                         event) -> None:
        x = self.btn.winfo_rootx() + self.btn.winfo_width()
        y = self.btn.winfo_rooty()
        self.btn.menu.tk_popup(x, y)
    
    def add_command(self, 
                    label: str, 
                    command) -> None:
        self.btn.menu.add_command(label=label, command=command)
    
    def add_separator(self) -> None:
        self.btn.menu.add_separator()
    
    def config(self,
               **kwargs):
        self.btn.config(**kwargs)


if __name__ == "__main__":
    from cpu_window import CPUWindow
    from ram_window import RAMWindow
    from net_window import NetWindow
    from disk_window import DiskWindow
    cpu = CPUWindow()
    ram = RAMWindow()
    net = NetWindow()
    disk = DiskWindow()
    tk.mainloop()