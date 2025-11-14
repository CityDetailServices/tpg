#!/usr/bin/env python3
"""
Manual bus stop logger with scheduled target times.

Press ENTER at each stop to log the actual arrival time. The script compares the
actual time to the scheduled (target) time and prints a tail view with deviations
and travel time between stops. Results are saved to 'bus_trip_log.csv'.
"""

from datetime import datetime
import csv

# ANSI color codes for terminal
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Stops with their scheduled target times (HH:MM)
bus_stops = [
    {"sequence": 1, "time": "09:43", "stop": "Grand-Lancy, Stade de Genève"},
    {"sequence": 2, "time": "09:45", "stop": "Lancy-Pont-Rouge, gare/Etoile"},
    {"sequence": 3, "time": "09:47", "stop": "Lancy-Pont-Rouge, gare"},
    {"sequence": 4, "time": "09:49", "stop": "Petit-Lancy, place"},
    {"sequence": 5, "time": "09:51", "stop": "Les Esserts"},
    {"sequence": 6, "time": "09:52", "stop": "Onex, Bandol"},
    {"sequence": 7, "time": "09:54", "stop": "Salle communale"},
    {"sequence": 8, "time": "09:55", "stop": "Conégnon, La Dode"},
    {"sequence": 9, "time": "09:56", "stop": "croisée"},
    {"sequence": 10, "time": "09:58", "stop": "Bernex, P+R"}
]

# Convert target times (HH:MM) to datetime objects for today
today = datetime.now()
for s in bus_stops:
    hh_mm = s["time"]
    s["target_time"] = datetime.strptime(hh_mm, "%H:%M").replace(
        year=today.year, month=today.month, day=today.day
    )

# Storage for actual logged times
actual_times = {}  # key: sequence (int) -> datetime

def format_deviation(actual_dt, target_dt):
    """Return (sign_str, minutes, seconds, total_seconds) for deviation"""
    total_seconds = int((actual_dt - target_dt).total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    sec_abs = abs(total_seconds)
    minutes = sec_abs // 60
    seconds = sec_abs % 60
    return sign, minutes, seconds, total_seconds

def color_for_deviation(total_seconds):
    if total_seconds > 0:
        return RED   # late
    elif total_seconds < 0:
        return GREEN # early
    else:
        return YELLOW # on time

def print_tail_view():
    print("\n--- Bus Trip Status ---")
    print(f"{'Seq':<3} {'Stop':<25} {'Target':<6} {'Actual':<8} {'Deviation':<12} {'From prev'}")
    prev_actual = None
    for s in bus_stops:
        seq = s["sequence"]
        name = s["stop"]
        target_str = s["target_time"].strftime("%H:%M")
        actual_dt = actual_times.get(seq)
        if actual_dt:
            actual_str = actual_dt.strftime("%H:%M:%S")
            sign, m, sec, total_sec = format_deviation(actual_dt, s["target_time"])
            color = color_for_deviation(total_sec)
            deviation_str = f"{sign}{m}m {sec}s"
            deviation_colored = f"{color}{deviation_str}{RESET}"
        else:
            actual_str = "-"
            deviation_colored = "-"

        # travel time from previous actual logged stop
        if actual_dt and prev_actual:
            travel_sec = int((actual_dt - prev_actual).total_seconds())
            tm = travel_sec // 60
            ts = travel_sec % 60
            travel_str = f"{tm}m {ts}s"
        else:
            travel_str = "-"

        print(f"{seq:<3} {name:<25} {target_str:<6} {actual_str:<8} {deviation_colored:<12} {travel_str}")
        if actual_dt:
            prev_actual = actual_dt
    print("-----------------------\n")

# CSV output file
output_csv = "bus_trip_log.csv"

print("Manual bus stop logger (with scheduled times)")
print("Press ENTER when the bus reaches each stop to log actual time.")
print("Script will show deviations vs scheduled times and travel time from previous stop.\n")

# Main loop: prompt user for each stop
for s in bus_stops:
    seq = s["sequence"]
    prompt = f"Press ENTER at stop {seq} - {s['stop']} (scheduled {s['time']}) -> "
    input(prompt)
    now = datetime.now()
    actual_times[seq] = now
    print(f"Logged: {s['stop']} at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # show tail view after each log
    print_tail_view()

# Save results to CSV
with open(output_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Sequence", "Stop", "Target Time", "Actual Time", "Deviation (+/-)", "Deviation Secs", "Travel From Prev"
    ])
    prev_actual = None
    for s in bus_stops:
        seq = s["sequence"]
        name = s["stop"]
        target_str = s["target_time"].strftime("%H:%M")
        actual_dt = actual_times.get(seq)
        if actual_dt:
            actual_str = actual_dt.strftime("%Y-%m-%d %H:%M:%S")   # ✅ fixed quotes here
            sign, m, sec, total_sec = format_deviation(actual_dt, s["target_time"])
            deviation_str = f"{sign}{m}m {sec}s"
        else:
            actual_str = ""
            deviation_str = ""
            total_sec = ""
        if actual_dt and prev_actual:
            travel_sec = int((actual_dt - prev_actual).total_seconds())
            travel_str = f"{travel_sec//60}m {travel_sec%60}s"
        else:
            travel_str = ""
        writer.writerow([seq, name, target_str, actual_str, deviation_str, total_sec, travel_str])
        if actual_dt:
            prev_actual = actual_dt

print(f"\nAll logged data saved to '{output_csv}'.")
