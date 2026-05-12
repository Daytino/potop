from main_window import MainWindow
import psutil, cpuinfo, time, datetime
import tkinter as tk

class CPUWindow(MainWindow):
    def __init__(self):
        self.title = "Температура процессора"
        self.start_time = time.time()
        super().__init__(window_type="CPU")
    
    def build_main_window(self):
        super().build_main_window()

        cpu_info = cpuinfo.get_cpu_info()
        cpu_model = cpu_info["brand_raw"]
        cpu_speed = cpu_info["hz_actual"][0] / 10 ** 9
        cpu_l2_cache_size = cpu_info["l2_cache_size"] / 2 ** 20
        cpu_l3_cache_size = cpu_info["l3_cache_size"] / 2 ** 20
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

        model_label = tk.Label(left_frame, text=f"Кэш L2: {cpu_l2_cache_size} MB", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        model_label.pack(anchor=tk.W)

        model_label = tk.Label(left_frame, text=f"Кэш L3: {cpu_l3_cache_size} MB", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        model_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.uptime_label = tk.Label(right_frame, text="Время работы: --", 
                                 font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.uptime_label.pack(anchor=tk.E)

        self.freq_label = tk.Label(right_frame, text="Частота: -- MHz", 
                                   font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.freq_label.pack(anchor=tk.E)
        
        self.percent_label = tk.Label(right_frame, text="Загрузка: --%", 
                                      font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.percent_label.pack(anchor=tk.E)
        
        self.avg_label = tk.Label(right_frame, text="Среднее: --%", 
                                  font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.avg_label.pack(anchor=tk.E)
        
        self.max_label = tk.Label(right_frame, text="Макс: --%", 
                                  font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.max_label.pack(anchor=tk.E)
        
        self.max_time_label = tk.Label(right_frame, text="Время макс: --", 
                                       font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.max_time_label.pack(anchor=tk.E)
    
    def update_plot_environment(self, y_min, y_max, y_delta):
        self.plot.set_xlabel("Время (s)", fontfamily='Consolas', fontsize=12)
        self.plot.set_ylabel("Загрузка (%)", fontfamily='Consolas', fontsize=12)
        self.plot.set_title("Загрузка процессора", fontfamily='Consolas', fontsize=12, fontweight='bold')
        return super().update_plot_environment(self.y_min, self.y_max, 2.5)

    def _cycle(self):
        cpu_percent = psutil.cpu_percent()
        
        if not hasattr(self, "y_max_value"):
            self.y_max_value = 0

        if cpu_percent > self.y_max_value:
            self.y_max_value = cpu_percent
            self.max_time = self.current_time + self.time_delta
            self.max_time_full = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            self.db.save_peak("CPU", self.y_max_value, self.max_time, self.max_time_full)
        
        super().update_plot(is_cut_left=True, new_y_value=cpu_percent)
        cpu_freq = psutil.cpu_freq().current
        
        valid_y = [v for v in self.y if v != self.y_min]
        avg_value = sum(valid_y) / len(valid_y) if valid_y else 0
        
        self.freq_label.config(text=f"Частота: {cpu_freq:.0f} MHz")
        self.percent_label.config(text=f"Загрузка: {cpu_percent}%")
        self.avg_label.config(text=f"Среднее: {avg_value:.1f}%")
        self.max_label.config(text=f"Максимальное значение: {self.y_max_value}%")
        self.max_time_label.config(text=f"Время максимального значения: {self.max_time_full} ({self.max_time:.0f} с)")
        
        super()._update_runtime_label(self.start_time)
        
        self._after_id = self.root.after(int(self.time_delta * 1000), self._cycle)
