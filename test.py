import cpuinfo, psutil
from pprint import pprint


cpu_info = cpuinfo.get_cpu_info()

cpu_model = cpu_info["brand_raw"]
cpu_arch = cpu_info["arch"]
cpu_cores = psutil.cpu_count(False)
cpu_threads = psutil.cpu_count(True)

while True
print(cpu_cores, cpu_threads)