# import cpuinfo
# import psutil
# import GPUtil
# from pprint import pprint
# import time


# cpu_info = cpuinfo.get_cpu_info()
# cpu_model = cpu_info["brand_raw"]
# cpu_arch = cpu_info["arch"]
# cpu_cores = psutil.cpu_count(False)
# cpu_threads = psutil.cpu_count(True)
# print(cpu_info)

# while True:
#     ram_info = psutil.virtual_memory()
#     ram_percent = ram_info.percent
#     ram_total = ram_info.total / 1024 ** 3
#     ram_free = ram_info.free / 1024 ** 3
#     ram_avail = ram_info.available / 1024 ** 3
#     ram_used = ram_info.used / 1024 ** 3
#     print(psutil.net_io_counters().bytes_sent)
#     print("------------------")
#     cpu_info = cpuinfo.get_cpu_info()

#     cpu_usage = psutil.cpu_freq().current
#     cpu_percent = psutil.cpu_percent()
#     #sniff(prn=lambda x: print(x.summary()), count=10)
#     #print(*[cpu_usage, cpu_percent, ram_used, ram_percent], sep="\n")
#     time.sleep(0.5)

# #print(cpu_model, cpu_arch, cpu_cores, cpu_threads)

import tkinter as tk
import typing
root = tk.Tk()

# Set title
root.title("Main Window")

# Set Geometry
root.geometry("200x200")

class MenubuttonBuilder:
    def __init__(self, parent: tk.Frame, 
                 text: str, 
                 is_menu_right: bool = False) -> None:
        btn = tk.Menubutton(parent, text=text)
        btn.menu = tk.Menu(btn, tearoff=False)
        btn["menu"] = btn.menu
        self.btn = btn

        if is_menu_right:
            btn.bind("<Button-1>", self._show_menu_right)
        
    def pack(self, 
             **kwargs) -> None:
        self.btn.pack(**kwargs)

    def _show_menu_right(self, 
                         event):
        x = self.btn.winfo_rootx() + self.btn.winfo_width()
        y = self.btn.winfo_rooty()
        self.btn.menu.tk_popup(x, y)
    
    def add_command(self, 
                    label: str, 
                    command) -> None:
        self.btn.menu.add_command(label=label, command=command)
    
    def add_separator(self):
        self.btn.menu.add_separator()


a = MenubuttonBuilder(root, "123", is_menu_right=True)
a.add_command("12", lambda: print(123))

a.pack()

b = MenubuttonBuilder(root, "321", is_menu_right=False)
b.add_command("32", lambda: print(321))

b.pack()


tk.mainloop()