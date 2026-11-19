import re
from pathlib import Path
from collections import defaultdict, Counter
from statistics import mean

# -----------------------------------------------------------------------------
# File Paths
# -----------------------------------------------------------------------------

script_dir = Path(__file__).parent

log_file = script_dir / "pract.txt"
report_file = script_dir / "CAN_Report.txt"

print("Using file:", log_file)

if not log_file.exists():
    print("ERROR: pract.txt not found")
    exit()

# -----------------------------------------------------------------------------
# Regex Pattern
# -----------------------------------------------------------------------------

pattern = re.compile(
    r"Timestamp:\s*([\d.]+)\s*\|\s*ID:\s*0x([0-9A-Fa-f]+)\s*\|\s*DLC:\s*(\d+)\s*\|\s*Data:\s*(.*)"
)

# -----------------------------------------------------------------------------
# Store Messages
# -----------------------------------------------------------------------------

messages = defaultdict(list)

with open(log_file, "r", errors="ignore") as f:

    for line in f:

        match = pattern.search(line)

        if not match:
            continue

        timestamp = float(match.group(1))
        can_id = int(match.group(2), 16)
        dlc = int(match.group(3))

        try:
            data = [int(x, 16) for x in match.group(4).split()]
        except:
            continue

        messages[can_id].append(
            {
                "timestamp": timestamp,
                "dlc": dlc,
                "data": data,
            }
        )

# -----------------------------------------------------------------------------
# Create Report
# -----------------------------------------------------------------------------

with open(report_file, "w") as report:

    report.write("=" * 80 + "\n")
    report.write("CAN LOG ANALYSIS REPORT\n")
    report.write("=" * 80 + "\n\n")

    total_frames = sum(len(v) for v in messages.values())

    report.write(f"Total Unique IDs : {len(messages)}\n")
    report.write(f"Total Frames     : {total_frames}\n\n")

    # -------------------------------------------------------------------------
    # ID Summary
    # -------------------------------------------------------------------------

    report.write("ID SUMMARY\n")
    report.write("-" * 80 + "\n")

    for can_id in sorted(messages):
     report.write(
        f"0x{can_id:08X}  Occurrences = {len(messages[can_id])}\n"
    )

    report.write("\n\n")

    # -------------------------------------------------------------------------
    # Per-ID Analysis
    # -------------------------------------------------------------------------

    for can_id in sorted(messages):

        frames = messages[can_id]

        report.write("=" * 80 + "\n")
        report.write(f"CAN ID : 0x{can_id:X}\n")
        report.write("=" * 80 + "\n")

        report.write(f"Occurrences : {len(frames)}\n\n")

        # ---------------------------------------------------------------------
        # DLC Distribution
        # ---------------------------------------------------------------------

        dlc_count = Counter(frame["dlc"] for frame in frames)

        report.write("DLC Distribution\n")
        report.write("-" * 40 + "\n")

        for dlc, count in sorted(dlc_count.items()):
            report.write(f"DLC {dlc:<3} -> {count}\n")

        # ---------------------------------------------------------------------
        # Cycle Time
        # ---------------------------------------------------------------------

        if len(frames) > 1:

            cycle_times = []

            for i in range(1, len(frames)):

                diff = (
                    frames[i]["timestamp"]
                    - frames[i - 1]["timestamp"]
                ) * 1000

                cycle_times.append(diff)

            report.write("\nTiming Information\n")
            report.write("-" * 40 + "\n")

            report.write(
                f"Average Cycle Time : {mean(cycle_times):.3f} ms\n"
            )

            report.write(
                f"Minimum Cycle Time : {min(cycle_times):.3f} ms\n"
            )

            report.write(
                f"Maximum Cycle Time : {max(cycle_times):.3f} ms\n"
            )

        # ---------------------------------------------------------------------
        # Byte Analysis
        # ---------------------------------------------------------------------

        max_dlc = max(frame["dlc"] for frame in frames)

        report.write("\nByte Analysis\n")
        report.write("-" * 40 + "\n")

        for byte_index in range(max_dlc):

            values = []

            for frame in frames:

                if byte_index < len(frame["data"]):
                    values.append(frame["data"][byte_index])

            if not values:
                continue

            unique_values = sorted(set(values))

            report.write(f"\nByte {byte_index}\n")

            # Constant Byte
            if len(unique_values) == 1:

                report.write(
                    f"Constant Value : 0x{unique_values[0]:02X}\n"
                )

            else:

                report.write(
                    f"Min Value      : 0x{min(unique_values):02X}\n"
                )

                report.write(
                    f"Max Value      : 0x{max(unique_values):02X}\n"
                )

                report.write(
                    f"Unique Values  : {len(unique_values)}\n"
                )

                # Rolling Counter Detection

                counter_hits = 0

                for i in range(1, len(values)):

                    if ((values[i] - values[i - 1]) % 256) == 1:
                        counter_hits += 1

                score = (
                    counter_hits / max(1, (len(values) - 1))
                ) * 100

                report.write(
                    f"Counter Score  : {score:.1f}%\n"
                )

                if score > 80:
                    report.write(
                        "Possible Rolling Counter\n"
                    )

        # ---------------------------------------------------------------------
        # Sample Frames
        # ---------------------------------------------------------------------

        report.write("\nSample Frames\n")
        report.write("-" * 40 + "\n")

        for frame in frames[:5]:

            data_str = " ".join(
                f"{b:02X}"
                for b in frame["data"]
            )

            report.write(
                f"{frame['timestamp']} | {data_str}\n"
            )

        report.write("\n\n")

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

print("\nAnalysis Complete")
print("Report saved at:")
print(report_file)

