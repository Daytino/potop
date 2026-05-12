from main_window import MainWindow
import psutil, time
import tkinter as tk

class RAMWindow(MainWindow):
    def __init__(self):
        self.title = "Использование оперативной памяти"
        self.start_time = time.time()
        super().__init__(window_type="RAM")
    
    def build_main_window(self):
        super().build_main_window()
        
        ram_info = psutil.virtual_memory()
        ram_total = ram_info.total / 1024 ** 3
        
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
        self.plot.set_xlabel("Время (s)", fontfamily='Consolas', fontsize=12)
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
        
        super()._update_runtime_label(self.start_time)
        
        self.root.after(int(self.time_delta * 1000), self._cycle)
