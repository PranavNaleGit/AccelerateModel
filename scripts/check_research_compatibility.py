import json
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "results" / "hardware-inventory.json"

def main():
    print("=== LocalCodeEngine Research Compatibility ===")

    if not INVENTORY.exists():
        print("ERROR: Hardware inventory is missing.")
        print("Run the hardware inventory command first.")
        return 1

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8-sig"))
    system = platform.system()
    disk = shutil.disk_usage(ROOT)

    gpu_entries = inventory.get("gpu", [])
    nvidia = [
        gpu for gpu in gpu_entries
        if "NVIDIA" in gpu.get("Name", "").upper()
    ]

    print(f"OS: {system} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Project disk free: {disk.free / (1024**3):.1f} GiB")
    print(f"System RAM: {inventory.get('system_ram_bytes', 0) / (1024**3):.1f} GiB")

    if nvidia:
        for gpu in nvidia:
            print(f"GPU: {gpu.get('Name')}")
            print(f"Windows-reported adapter memory: {gpu.get('AdapterRAM')}")
    else:
        print("WARNING: NVIDIA GPU was not found in the inventory.")

    print("\n=== Research candidate: DC-Leap ===")
    print("Checkpoint family: LLaDA / Dream diffusion language models")
    print("Official requirements include PyTorch and flash-attention.")
    print("Status: COMPATIBILITY NOT YET VERIFIED")

    if system == "Windows":
        print("WARNING: Check the project's Linux/CUDA build requirements.")
        print("Do not assume flash-attention will install on native Windows.")

    if nvidia:
        print("WARNING: 6 GB VRAM is a tight constraint for the listed 7B/8B models.")
        print("Model weights, attention cache, and temporary tensors need memory.")
        print("Quantization or offloading is not assumed to be supported.")

    print("\nNext action: inspect the official runtime and model requirements.")
    print("No packages or model files were installed by this script.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
