import subprocess

#### sending a single command
p = subprocess.run('ls', shell=True, check=True, capture_output=True, encoding='utf-8')
print(f'Command \"{p.args}\" exited with returncode {p.returncode}, output: \n{p.stdout}')


#### sending multiple commands at once
commands = "cd test; mkdir test_in_test; ls"
p = subprocess.run(commands, shell=True, check=True, capture_output=True, encoding='utf-8')
print(f'Command \"{p.args}\" exited with returncode {p.returncode}, output: \n{p.stdout}')


#### multiple commands after one another

commands = ["pwd", "ls", "cd test", "mkdir test_nacheinander", "ls", "sudo pip install numpy"]

# with subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as shell:
with subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as shell:
    for idx, command in enumerate(commands):
        print(f"\nExecuting command {idx + 1}: {command}")
        # Send command to the shell
        shell.stdin.write(command + "\n")
        shell.stdin.flush()

        # Wait for the command to finish and capture its output
        shell.stdin.write("echo $? > /tmp/last_exit_code\n")
        #shell.stdin.flush()
        shell.stdin.write("cat /tmp/last_exit_code\n")
        shell.stdin.flush()

        # Read command output until EOF (or next prompt)
        stdout_lines = []
        stderr_lines = []
        while True:
            line = shell.stdout.readline()
            stdout_lines.append(line)
            # line_err = shell.stderr.readline()
            # stderr_lines.append(str(line_err))

            
            # print(shell.stdout,shell.stderr)
            if line.startswith("0") or line.startswith("1") or line== (''):
                break

            
        print("". join(stdout_lines))
        # print("". join(stderr_lines))
        