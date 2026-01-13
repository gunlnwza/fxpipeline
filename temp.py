from rich.console import Console
from rich.status import Status
import time

console = Console()

status = Status("Starting…", spinner="dots", console=console)
status.start()

for i in range(5):
    status.update(f"Pulling layer {i+1}/5")
    time.sleep(1)
    console.print(f"✔ Pulled layer {i+1}/5")

status.stop()
console.print("[bold green]Done!")