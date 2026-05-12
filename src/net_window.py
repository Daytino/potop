from main_window import MainWindow
import tkinter as tk
import psutil, time, configparser, numpy as np, threading
from typing import Union
from main_window import MenubuttonBuilder


class NetWindow(MainWindow):
    def __init__(self) -> None:
        self.title = "Скорость сети"
        self.start_time = time.time()
        self.collector = None
        self._init_collector()
        super().__init__(window_type="Net")
    
    def _init_collector(self):
        net_info = psutil.net_if_stats()
        for interface, stats in net_info.items():
            if stats.isup and "loop" not in interface.lower():
                self.interface = interface
                self.collector = NetDataCollector(interface)
                self.collector.start()
                break
        else:
            self.interface = "Нет сети"
    
    def build_main_window(self) -> None:
        super().build_main_window()
        
        self.canvas.get_tk_widget().pack_forget()
        
        self.info_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=1)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(self.info_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        info_frame_size = 12
        info_frame_family = "Consolas"
        
        net_info = psutil.net_if_stats()
        interface_frame = tk.Frame(left_frame)
        interface_frame.pack(anchor=tk.W)
        
        interface_btn = MenubuttonBuilder(interface_frame, self.interface, True, borderwidth=0,
                                          fg="#0366d6", background="#f0f0f0", highlightbackground="#E2E2E2",
                                          relief=tk.SOLID, cursor="hand2", font=("Consolas", 12, "underline", "bold"))

        for interface, stats in net_info.items():
            if stats.isup and "loop" not in interface.lower():
                interface_btn.add_command(label=interface, command=lambda i=interface: self.change_interface(i))

        interface_btn.pack(side=tk.RIGHT, pady=(0, 2))

        interface_label = tk.Label(interface_frame, text=f"Интерфейс:", 
                              font=(info_frame_family, info_frame_size, "bold"), anchor=tk.W)
        interface_label.pack(anchor=tk.W)
        
        addrs = psutil.net_if_addrs().get(self.interface, [])
        ipv4 = next((addr.address for addr in addrs if addr.family == 2), "N/A")
        
        self.ip_label = tk.Label(left_frame, text=f"IPv4: {ipv4}", 
                           font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.ip_label.pack(anchor=tk.W)
        
        self.sent_label = tk.Label(left_frame, text="Отправлено: -- MB", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.sent_label.pack(anchor=tk.W)
        
        self.recv_label = tk.Label(left_frame, text="Получено: -- MB", 
                              font=(info_frame_family, info_frame_size), anchor=tk.W)
        self.recv_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.uptime_label = tk.Label(right_frame, text="Время работы: --", 
                                 font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.uptime_label.pack(anchor=tk.E)
        
        self.speed_recv_label = tk.Label(right_frame, text="Загрузка: -- KB/s", 
                                   font=(info_frame_family, info_frame_size), anchor=tk.E)
        self.speed_recv_label.pack(anchor=tk.E)
        
        self.speed_sent_label = tk.Label(right_frame, text="Отправка: -- KB/s", 
                                      font=(info_frame_family, info_frame_size), anchor=tk.E, fg="#689d6a")
        self.speed_sent_label.pack(anchor=tk.E)
        self.interface_label = interface_label
        self.interface_btn = interface_btn
    
    def update_plot_environment(self, y_min, y_max, y_delta) -> None:
        self.plot.set_xlabel("Время (s)", fontfamily='Consolas', fontsize=12)
        self.plot.set_ylabel("Скорость (KB/s)", fontfamily='Consolas', fontsize=12)
        self.plot.set_title("Сетевая активность", fontfamily='Consolas', fontsize=12, fontweight='bold')
        return super().update_plot_environment(y_min, y_max, y_delta)
    
    def change_interface(self, interface_name: str):
        self.interface = interface_name
        self.interface_btn.config(text=interface_name)
        
        addresses = psutil.net_if_addrs().get(interface_name, [])
        ipv4_address = next((address.address for address in addresses if address.family == 2), "N/A")
        self.ip_label.config(text=f"IPv4: {ipv4_address}")
        
        if self.collector:
            self.collector.stop()
        self.collector = NetDataCollector(interface_name)
        self.collector.start()

    def _cycle(self) -> None:
        if self.collector:
            sent_speed = self.collector.sent_speed
            recv_speed = self.collector.recv_speed
            super().update_plot(is_cut_left=True, 
                              new_y_value=recv_speed, 
                              new_y_value_sent=sent_speed)
            
            self.sent_label.config(text=f"Отправлено: {self.collector.total_sent / 1024 ** 2:.1f} MB")
            self.recv_label.config(text=f"Получено: {self.collector.total_recv / 1024 ** 2:.1f} MB")
            self.speed_recv_label.config(text=f"Загрузка: {recv_speed:.1f} KB/s")
            self.speed_sent_label.config(text=f"Отправка: {sent_speed:.1f} KB/s")
        
        super()._update_runtime_label(self.start_time)
    
    def _cleanup(self):
        super()._cleanup()
        if self.collector:
            self.collector.stop()


class NetDataCollector(threading.Thread):
    def __init__(self, interface):
        super().__init__(daemon=True)
        self.interface = interface
        self._read_config("src/potop.cfg")
        
        self.sent_speed = 0
        self.recv_speed = 0
        self.total_sent = 0
        self.total_recv = 0
        
        self._stop_event = threading.Event()
        
        net = psutil.net_io_counters()
        self.old_bytes_sent = net.bytes_sent
        self.old_bytes_recv = net.bytes_recv
    
    def _read_config(self, config_path):
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path)
        section = "Window.Net"
        self.y_min = config.getint(section, "y_min")
        self.x_range = config.getint(section, "x_range")
        self.time_delta = config.getfloat("Time", "time_delta")
    
    def run(self):
        while not self._stop_event.is_set():
            net_info = psutil.net_io_counters()
            
            sent_delta = net_info.bytes_sent - self.old_bytes_sent
            recv_delta = net_info.bytes_recv - self.old_bytes_recv
            
            self.old_bytes_sent = net_info.bytes_sent
            self.old_bytes_recv = net_info.bytes_recv
            
            self.sent_speed = sent_delta / 1024 / self.time_delta
            self.recv_speed = recv_delta / 1024 / self.time_delta
            self.total_sent = net_info.bytes_sent
            self.total_recv = net_info.bytes_recv
            
            self._stop_event.wait(self.time_delta)
    
    def stop(self):
        self._stop_event.set()


if __name__ == "__main__":
    NetWindow()
    tk.mainloop()