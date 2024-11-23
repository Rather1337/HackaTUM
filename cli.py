import subprocess

class CLI():
    def __init__(self):
        self.shell = subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def execute(self, cmd):
        print(f"Executing command: '{cmd}'")
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
        
        

        return self._reformat(stdout_lines)
        # print("". join(stdout_lines))
        # print("". join(stderr_lines))

    def _reformat(self, msg:list):
        messages = msg[:-1]
        messages = "; ".join(messages)
        return(messages, int(msg[-1]))
        