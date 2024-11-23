import subprocess

p = subprocess.run('sudo pip install numpy', shell=True, check=True, capture_output=True, encoding='utf-8')

print(f'Command \"{p.args}\" exited with returncode {p.returncode}, output: \n{p.stdout}')
