import psutil
import sys

sys.path.append('./utils')  

pid = 0

list_pid = psutil.pids()
for pid in list_pid:
    try:
        p = psutil.Process(pid)
        if "aplay" in p.name():
            print('*' * 30)
            print("Nombre:", p.name())
            print("PID:", pid)
            print("EXE:", p.exe())
            print("CWD:", p.cwd())
            print("CL:", p.cmdline())
            print("ST:", p.status())
    except (psutil.ZombieProcess, psutil.AccessDenied, psutil.NoSuchProcess):
        pass
