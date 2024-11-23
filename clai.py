import subprocess
import os
from agent import Agent
from cli import CLI

num_retries = 10

def main():

    with open("doc.txt", "r") as file:
        doc_content = file.read() # TODO make with launch args and more versatile, add cases e.g. URL or pdf etc.

    agent = Agent(doc_content)
    cli = CLI()

    last_failed = False

    response = ["", ""]
    while(True):
        if not last_failed:
            cmd = agent.get_next_cmd()
        else:
            cmd = agent.retry_cmd(response[0])
            last_failed = False

        print(cmd)

        if cmd == 'done':
            break
        else:
            response = cli.execute(cmd)
            print(response)
            if response[-1] != 0:
                last_failed = True

    return 0

if __name__ == "__main__":
    main()