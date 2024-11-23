import subprocess

#### sending a single command
p = subprocess.run('ls', shell=True, check=True, capture_output=True, encoding='utf-8')
print(f'Command \"{p.args}\" exited with returncode {p.returncode}, output: \n{p.stdout}')


#### sending multiple commands at once
commands = "cd test; mkdir test_in_test; ls"
p = subprocess.run(commands, shell=True, check=True, capture_output=True, encoding='utf-8')
print(f'Command \"{p.args}\" exited with returncode {p.returncode}, output: \n{p.stdout}')


#### multiple commands after one another
p = subprocess.Popen("bash", shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

commands = ["pwd", "ls", "cd test", "mkdir test_nacheinander", "ls", "sudo pip install numpy"]

for cmd in commands:
    p.stdin.write(cmd+"\n")
    p.stdin.flush()
    # p.wait()
    print(p.stdout.readline())