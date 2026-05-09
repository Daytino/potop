import cpuinfo
import psutil
import GPUtil
from pprint import pprint
import time

cpu_info = cpuinfo.get_cpu_info()
cpu_model = cpu_info["brand_raw"]
cpu_arch = cpu_info["arch"]
cpu_cores = psutil.cpu_count(False)
cpu_threads = psutil.cpu_count(True)

while True:
    ram_info = psutil.virtual_memory()
    ram_percent = ram_info.percent
    ram_total = ram_info.total / 1024 ** 3
    ram_free = ram_info.free / 1024 ** 3
    ram_avail = ram_info.available / 1024 ** 3
    ram_used = ram_info.used / 1024 ** 3

    cpu_info = cpuinfo.get_cpu_info()

    cpu_usage = psutil.cpu_freq().current
    cpu_percent = psutil.cpu_percent()
    #sniff(prn=lambda x: print(x.summary()), count=10)
    print(*[cpu_usage, cpu_percent, ram_used, ram_percent], sep="\n")
    time.sleep(0.5)

#print(cpu_model, cpu_arch, cpu_cores, cpu_threads)
