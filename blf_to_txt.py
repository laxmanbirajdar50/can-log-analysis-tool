import can
from pathlib import Path

blf_file = Path("ECU_log.blf")
txt_file = Path("converted_log.txt")

if not blf_file.exists():
    print(f"Error: {blf_file} not found.")
    exit()

with open(txt_file, "w") as f:
    for msg in can.BLFReader(str(blf_file)):
        f.write(
            f"Timestamp: {msg.timestamp:.6f} | "
            f"ID: 0x{msg.arbitration_id:08X} | "
            f"DLC: {msg.dlc:02d} | "
            f"Data: {msg.data.hex(' ')}\n"
        )

print("Conversion completed successfully.")
print(f"Output file: {txt_file}")