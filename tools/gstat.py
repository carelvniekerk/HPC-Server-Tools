import time
import curses
import psutil
import argparse
from gpustat import new_query

def get_gpu_info(selected_gpus):
    gpu_stats = new_query()
    gpu_info = []
    for gpu in gpu_stats.gpus:
        if gpu.index in selected_gpus:
            jobs = [p for p in gpu.processes if p['username'] != 'root']
            info = {
                "index": gpu.index,
                "name": gpu.name,
                "memory_total": gpu.memory_total,
                "memory_used": gpu.memory_used,
                "memory_free": gpu.memory_free,
                "temperature": gpu.temperature,
                "utilization": gpu.utilization,
                "jobs": jobs
            }
            gpu_info.append(info)
    return gpu_info

def get_cpu_info():
    return psutil.cpu_percent(interval=1)

def get_cpu_temp():
    try:
        return psutil.sensors_temperatures()['coretemp'][0].current
    except (KeyError, IndexError):
        return None

def get_ram_info():
    ram = psutil.virtual_memory()
    return ram.total, ram.used, ram.free

def get_cpu_architecture():
    return psutil.cpu_info().arch

def color_value(stdscr, value, thresholds, colors):
    if value < thresholds[0]:
        color = colors[0]
    elif value < thresholds[1]:
        color = colors[1]
    else:
        color = colors[2]
    stdscr.attron(color)
    stdscr.addstr(f"{value}")
    stdscr.attroff(color)

def display_info(stdscr, selected_gpus):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)  # Headers
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # Low usage
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Medium usage
    curses.init_pair(4, curses.COLOR_RED, -1)  # High usage
    curses.init_pair(5, curses.COLOR_BLUE, -1)  # Bold headers
    curses.init_pair(6, curses.COLOR_BLACK, -1)
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)

    while True:
        stdscr.clear()

        # Get CPU and RAM info
        cpu_usage = get_cpu_info()
        cpu_temp = get_cpu_temp()
        cpu_arch = get_cpu_architecture()
        ram_total, ram_used, ram_free = get_ram_info()

        # Get GPU info
        gpu_info = get_gpu_info(selected_gpus)

        # Display CPU architecture
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(0, 0, "CPU: ")
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(f"{cpu_arch}\n")

        # Display CPU info
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr("CPU Usage: ")
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        color_value(stdscr, cpu_usage, [50, 75], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
        stdscr.addstr("%\n")

        if cpu_temp:
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr("CPU Temperature: ")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            color_value(stdscr, cpu_temp, [60, 80], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
            stdscr.addstr(" C\n")

        # Display RAM info
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr("RAM Usage: ")
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        color_value(stdscr, ram_used // (1024 ** 2), [ram_total // (1024 ** 2) * 0.5, ram_total // (1024 ** 2) * 0.75], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
        stdscr.addstr(f"/{ram_total // (1024 ** 2)} MB\n")

        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr("RAM Free: ")
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        color_value(stdscr, ram_free // (1024 ** 2), [ram_total // (1024 ** 2) * 0.5, ram_total // (1024 ** 2) * 0.25], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
        stdscr.addstr(" MB\n")

        # Display GPU info
        row = 6
        for gpu in gpu_info:
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row, 0, f"GPU {gpu['index']}: {gpu['name']}\n")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row + 1, 0, "Memory Usage: ")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            color_value(stdscr, gpu['memory_used'], [gpu['memory_total'] * 0.5, gpu['memory_total'] * 0.75], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
            stdscr.addstr(f"/{gpu['memory_total']} MB\n")

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row + 2, 0, "Memory Free: ")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            color_value(stdscr, gpu['memory_free'], [gpu['memory_total'] * 0.5, gpu['memory_total'] * 0.25], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
            stdscr.addstr(" MB\n")

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row + 3, 0, "Temperature: ")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            color_value(stdscr, gpu['temperature'], [60, 80], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
            stdscr.addstr(" C\n")

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row + 4, 0, "Utilization: ")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            color_value(stdscr, gpu['utilization'], [50, 75], [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)])
            stdscr.addstr("%\n")

            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(row + 5, 0, "Non-root jobs:\n")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            for job in gpu['jobs']:
                stdscr.addstr(row + 6, 0, f"  - {job['username']} (PID: {job['pid']}, Mem: {job['gpu_memory_usage'] // (1024 ** 2)} MB)\n")
                row += 1
            row += 7

        stdscr.refresh()

        # Exit if 'q' is pressed
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor CPU, RAM, and GPU usage")
    parser.add_argument('--id', type=int, nargs='+', help='List of GPU indices to monitor', required=True)
    args = parser.parse_args()

    curses.wrapper(display_info, args.id)