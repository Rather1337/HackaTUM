from rich.console import Console
from rich.text import Text
import subprocess

console = Console()

console.print("Hello Developer! I am [bold green]clai[/bold green], your personal AI onboarding assistant.", style="bold")

# Run a shell command
try:
    result = subprocess.run(
        ["ls", "-la"],  # Example command
        text=True,
        capture_output=True,
        check=True,  # Raise an error if the command fails
    )
    # Print the command output using Rich
    console.print(Text(result.stdout, style="cyan"))
except subprocess.CalledProcessError as e:
    console.print(f"[bold red]Error:[/bold red] Command failed with exit code {e.returncode}", style="red")
except FileNotFoundError as e:
    console.print(f"[bold red]Error:[/bold red] {e}", style="red")




