import subprocess
import os
from agent import Agent
from cli import CLI

num_retries = 10

def fetch_document():
    while(True):
        try:
            path = input("Enter path to the document: ")

            with open(f"{path}", "r") as file:
                doc_content = file.read() # TODO make with launch args and more versatile, add cases e.g. URL or pdf etc.
            return doc_content
        except:
            print("No such file or directory")

def main():

    cli = CLI()

    doc_content = fetch_document()

    agent = Agent(doc_content)
    
    cli.print_start()

    last_failed = False

    response = ["", ""]
    while(True):
        if not last_failed:
            cmd = agent.get_next_cmd(response[0])
        else:
            cmd = agent.retry_cmd(response[0])
            last_failed = False

        cmd = cmd.strip('"')

        if cmd == 'done':
            break
        else:
            response = cli.execute(cmd)
            if response[-1] != 0:
                last_failed = True

    cli.print_end()
    return 0

if __name__ == "__main__":
    main()