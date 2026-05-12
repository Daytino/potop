from main_window import MainWindow
import psutil, time
import tkinter as tk

class DiskWindow(MainWindow):
    def __init__(self):
        self.title = "Загрузка диска"
        self.start_time = time.time()
        super().__init__(window_type="Disk")
    
    def build_main_window(self):
        super().build_main_window()
        
        disk = psutil.disk_partitions()[0].device
        disk_usage = psutil.disk_usage('/')
        disk_total = disk_usage.total / 1024**3
        
        self.canvas.get_tk_widget().pack_forget()
        
        self.info_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=1)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(self.info_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        info_frame_size = 12
        info_frame_family = "Consolas"
        
        disk_label = tk.Label(left_frame, text=f"Диск: {disk}  Всего: {disk_total:.1f} GB", 
                              font=(info_frame_family, info_frame_size, "bold"), anchor=tk.W)
        disk_label.pack(anchor=tk.W)
        
        self.read_label = tk.Label(left_frame, text="Чтение: -- MB/s", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.read_label.pack(anchor=tk.W)
        
        self.write_label = tk.Label(left_frame, text="Запись: -- MB/s", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.write_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.uptime_label = tk.Label(right_frame, text="Время работы: --", 
                                 font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.uptime_label.pack(anchor=tk.E)
        
        self.usage_label = tk.Label(right_frame, text="Занято: --%", 
                                   font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.usage_label.pack(anchor=tk.E)
        
        self.free_label = tk.Label(right_frame, text="Свободно: -- GB", 
                                      font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.free_label.pack(anchor=tk.E)
        
        self.old_read_bytes = psutil.disk_io_counters().read_bytes
        self.old_write_bytes = psutil.disk_io_counters().write_bytes
    
    def update_plot_environment(self, y_min, y_max, y_delta):
        self.plot.set_xlabel("Время (с)", fontfamily='Consolas', fontsize=12)
        self.plot.set_ylabel("Скорость (MB/s)", fontfamily='Consolas', fontsize=12)
        self.plot.set_title("Загрузка диска", fontfamily='Consolas', fontsize=12, fontweight='bold')
        return super().update_plot_environment(self.y_min, self.y_max, self.y_delta)
    
    def _cycle(self):
        disk = psutil.disk_io_counters()
        
        read_delta = disk.read_bytes - self.old_read_bytes
        write_delta = disk.write_bytes - self.old_write_bytes
        
        self.old_read_bytes = disk.read_bytes
        self.old_write_bytes = disk.write_bytes
        
        read_speed = read_delta / 1024 ** 2 / self.time_delta
        write_speed = write_delta / 1024 ** 2 / self.time_delta
        
        total_speed = read_speed + write_speed


        super().update_plot(is_cut_left=True, new_y_value=total_speed)
        
        disk_usage = psutil.disk_usage('/')
        disk_free = disk_usage.free / 1024 ** 3
        
        self.read_label.config(text=f"Чтение: {read_speed:.1f} MB/s")
        self.write_label.config(text=f"Запись: {write_speed:.1f} MB/s")
        self.usage_label.config(text=f"Занято: {disk_usage.percent}%")
        self.free_label.config(text=f"Свободно: {disk_free:.1f} GB")
        
        super()._update_runtime_label(self.start_time)
        
        self.root.after(int(self.time_delta * 1000), self._cycle)
