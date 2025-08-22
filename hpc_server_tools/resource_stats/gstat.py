# coding=utf-8
# --------------------------------------------------------------------------------
# Project: Hilbert HPC Server Tools
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
#
# This code was generated with the help of AI writing assistants
# including GitHub Copilot, ChatGPT, Bing Chat.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Display node statistics."""

import argparse
import curses
import platform

import psutil
from gpustat import new_query


def get_gpu_info(selected_gpus: list[str]) -> list[dict[str, int | str | float | list]]:
    """Get GPU usage information."""
    gpu_stats = new_query()
    gpu_info: list[dict[str, int | str | float | list]] = []
    for gpu in gpu_stats.gpus:
        if gpu.index in selected_gpus:
            jobs: list = [p for p in gpu.processes if p["username"] != "root"]
            info = {
                "index": gpu.index,
                "name": gpu.name,
                "memory_total": gpu.memory_total,
                "memory_used": gpu.memory_used,
                "temperature": gpu.temperature,
                "utilization": gpu.utilization,
                "jobs": jobs,
            }
            gpu_info.append(info)
    return gpu_info


def get_cpu_info() -> tuple[float, float, int, int, str]:
    """Get CPU and RAM usage information."""
    cpu_usage: float = psutil.cpu_percent(interval=1)
    try:
        temperature: float = psutil.sensors_temperatures()["coretemp"][0].current  # type: ignore[attr-defined] # This is only available if the system allows temperature monitoring
    except (KeyError, IndexError):
        temperature = -1.0

    ram_stats = psutil.virtual_memory()
    ram_total: int = ram_stats.total
    ram_used: int = ram_stats.used

    architecture = platform.processor()

    return cpu_usage, temperature, ram_total, ram_used, architecture


def color_value(
    stdscr,  # noqa: ANN001
    value: float,
    thresholds: list[float],
    colors: list,
) -> None:
    """Color the value based on thresholds."""
    if value < thresholds[0]:
        color = colors[0]
    elif value < thresholds[1]:
        color = colors[1]
    else:
        color = colors[2]
    stdscr.attron(color)
    stdscr.addstr(f"{value}")
    stdscr.attroff(color)


def display_info(stdscr, selected_gpus: list[str]) -> None:  # noqa: ANN001, PLR0915
    """Display CPU, RAM, and GPU usage information."""
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
        cpu_usage, cpu_temp, ram_total, ram_used, cpu_arch = get_cpu_info()

        # Display CPU architecture
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(0, 0, "CPU: ")
        stdscr.addstr(f"{cpu_arch}\n")
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        # Display CPU info
        stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
        stdscr.addstr("Utilisation: ")
        stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
        color_value(
            stdscr,
            cpu_usage,
            [50, 75],
            [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)],
        )
        stdscr.addstr("%\n")

        if cpu_temp >= 0.0:
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr("Temperature: ")
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
            color_value(
                stdscr,
                cpu_temp,
                [60, 80],
                [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)],
            )
            stdscr.addstr(" C\n")

        # Display RAM info
        stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
        stdscr.addstr("RAM Usage: ")
        stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
        color_value(
            stdscr,
            ram_used // (1024**2),
            [ram_total // (1024**2) * 0.5, ram_total // (1024**2) * 0.75],
            [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)],
        )
        stdscr.addstr(f"/{ram_total // (1024**2)} MB\n")

        if selected_gpus:
            # Get GPU info
            gpu_info: list[dict[str, int | str | float | list]] = get_gpu_info(
                selected_gpus,
            )

            # Display GPU info
            row = 5
            for gpu in gpu_info:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
                stdscr.addstr(row, 0, f"GPU {gpu['index']}: {gpu['name']}\n")
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

                stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr(row + 1, 0, "Utilisation: ")
                stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
                color_value(
                    stdscr=stdscr,
                    value=gpu["utilization"],  # type: ignore[arg-type] # Utilization is always a float
                    thresholds=[50, 75],
                    colors=[
                        curses.color_pair(2),
                        curses.color_pair(3),
                        curses.color_pair(4),
                    ],
                )
                stdscr.addstr("%\n")

                stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr(row + 2, 0, "Temperature: ")
                stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
                color_value(
                    stdscr=stdscr,
                    value=gpu["temperature"],  # type: ignore[arg-type] # Utilization is always a float
                    thresholds=[60, 80],
                    colors=[
                        curses.color_pair(2),
                        curses.color_pair(3),
                        curses.color_pair(4),
                    ],
                )
                stdscr.addstr(" C\n")

                stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr(row + 3, 0, "Memory Usage: ")
                stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
                color_value(
                    stdscr,
                    gpu["memory_used"],  # type: ignore[arg-type] # Utilization is always a float
                    [gpu["memory_total"] * 0.5, gpu["memory_total"] * 0.75],  # type: ignore[operator] # Memory usage is always a int
                    [curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)],
                )
                stdscr.addstr(f"/{gpu['memory_total']} MB\n")

                stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr(row + 4, 0, "Non-root jobs:\n")
                stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
                stdscr.attron(curses.color_pair(6))
                for job in gpu["jobs"]:  # type: ignore[union-attr] # Jobs is always a list
                    stdscr.addstr(
                        row + 5,
                        0,
                        f"  - {job['username']} (Mem: {job['gpu_memory_usage']} MB)\n",  # type: ignore[index]
                    )
                    row += 1
                stdscr.attroff(curses.color_pair(6))
                row += 6

        stdscr.refresh()

        # Exit if 'q' is pressed
        key = stdscr.getch()
        if key == ord("q"):
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor CPU, RAM, and GPU usage")
    parser.add_argument(
        "--id",
        type=str,
        help="List of GPU indices to monitor",
        default="",
    )
    args = parser.parse_args()

    args.id = args.id.split(" ") if args.id else []
    args.id = [int(i) for i in args.id if i.isdigit()]

    curses.wrapper(display_info, args.id)
