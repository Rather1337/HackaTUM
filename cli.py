import subprocess
from rich.console import Console
from rich.text import Text

class CLI():
    def __init__(self):
        self.shell = subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.console = Console()
        self.console.print("Hello Developer! I am [bold magenta]clai[/bold magenta], your personal AI onboarding assistant.", style="white")

    def execute(self, cmd):
        self.console.print(f"Executing command: '{cmd}'", style="white")
        self.shell.stdin.write(cmd + "\n")
        self.shell.stdin.flush()

        # Wait for the command to finish and capture its output
        self.shell.stdin.write("echo $? > /tmp/last_exit_code\n")
        self.shell.stdin.write("cat /tmp/last_exit_code\n")
        self.shell.stdin.flush()

        # Read command output until EOF (or next prompt)
        stdout_lines = []
        while True:
            line = self.shell.stdout.readline()
            stdout_lines.append(line[:-1]) # -1 to remove the \n

            if line.startswith("0") or line.startswith("1") or line== (''):
                break
        
        response = self._reformat(stdout_lines) # TODO use Rich

        self.console.print(f"The response was {response}", style="{}".format("green" if response[-1] == 0 else "red"))
        
        return response

    def _reformat(self, msg:list):
        messages = msg[:-1]
        messages = "; ".join(messages)
        return(messages, int(msg[-1]))
    
    def print_end(self):
        self.console.print("All instructions were [bold green]successfully executed[/bold green].\nGoodbye! I hope you found this helpful.", style="white")

    def print_start(self):
        self.console.print("Running instructions...", style="italic")