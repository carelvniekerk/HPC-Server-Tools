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

def get_ram_info():
    ram = psutil.virtual_memory()
    return ram.total, ram.used, ram.free

def display_info(stdscr, selected_gpus):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_BLACK, -1)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)

    while True:
        stdscr.clear()

        # Get CPU and RAM info
        cpu_usage = get_cpu_info()
        ram_total, ram_used, ram_free = get_ram_info()

        # Get GPU info
        gpu_info = get_gpu_info(selected_gpus)

        # Display CPU info
        stdscr.addstr(0, 0, "CPU Usage: ", curses.color_pair(1))
        stdscr.addstr("{}".format(cpu_usage), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr("%", curses.color_pair(1))

        # Display RAM info
        stdscr.addstr(2, 0, "RAM Usage: ", curses.color_pair(2))
        stdscr.addstr("{}/{} MB".format(ram_used // (1024 ** 2), ram_total // (1024 ** 2)), curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(3, 0, "RAM Free: ", curses.color_pair(2))
        stdscr.addstr("{} MB".format(ram_free // (1024 ** 2)), curses.color_pair(2) | curses.A_BOLD)

        # Display GPU info
        row = 5
        for gpu in gpu_info:
            stdscr.addstr(row, 0, "GPU {}: {}".format(gpu['index'], gpu['name']), curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(row + 1, 0, "Memory Usage: ", curses.color_pair(7))
            stdscr.addstr("{}/{} MB".format(gpu['memory_used'], gpu['memory_total']), curses.color_pair(7) | curses.A_BOLD)
            stdscr.addstr(row + 2, 0, "Memory Free: ", curses.color_pair(7))
            stdscr.addstr("{} MB".format(gpu['memory_free']), curses.color_pair(7) | curses.A_BOLD)
            stdscr.addstr(row + 3, 0, "Temperature: ", curses.color_pair(4))
            stdscr.addstr("{} C".format(gpu['temperature']), curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(row + 4, 0, "Utilization: ", curses.color_pair(2))
            stdscr.addstr("{}%".format(gpu['utilization']), curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(row + 5, 0, "Non-root jobs:", curses.color_pair(6) | curses.A_BOLD)
            for job in gpu['jobs']:
                stdscr.addstr(row + 6, 0, "  - {} (PID: {}, Mem: {} MB)".format(job['username'], job['pid'], job['gpu_memory_usage'] // (1024 ** 2)), curses.color_pair(6))
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

