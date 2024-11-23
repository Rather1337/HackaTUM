import subprocess
import os
from agent import Agent
from CLI import CLI

num_retries = 10

def documentation_to_list(doc: str) -> list[str]:
    """Runs inference on a large text of documentation and returns a list of commands that are needed to complete the procedure.

    Args:
        doc (str): string of the text file

    Returns:
        list[str]: command list
    """
    return None


def run_inference(text) -> str:
    """Run inference of a text piece.

    Args:
        text (_type_): the text that acts as the input of the LLM.

    Returns:
        str: returns a command
    """
    # run inference on result and get one command to resolve the problem
    return None


def handle_failed_command(result) -> bool:
    """Run inference on failed command and try x-times to resolve it.

    Args:
        result (_type_): result of the failed command

    Returns:
        bool: success of resolving failed command
    """
    trial_count = 0

    while trial_count < num_retries:
        if evaluate_result(run_command(run_inference(result))):
            return True

        trial_count += 1

    return False


def run_command(command):
    """Runs one command in a terminal subprocess.

    Args:
        command (_type_): command that is going to be run

    Returns:
        _type_: to-be-determined
    """
    return subprocess.run(command, capture_output=True, text=True).stdout


def evaluate_result(result) -> bool:
    """Check if a command succeded.

    Args:
        result (_type_): terminal output

    Returns:
        bool: command successful or not
    """
    return None


def run_procedure(commands: list[str]) -> bool:
    """Main function that runs the full procedure given a list of commands.

    Args:
        commands (list[str]): List of commands.

    Returns:
        bool: if procedure succeded
    """

    for command in commands:
        result = run_command(command)
        evaluation = evaluate_result(result)
        if evaluation:
            continue
        else:
            if handle_failed_command(result):
                return True
            else:
                return False



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
            if response[-1] != 0:
                last_failed = True

    # LLM wrapper object init 
    # Add tutorial from file to LLM
    # Loop:
    #   LLM.get_next_cmd() -> str (command) # ask LLM for next command to execute
    #   run_command(command) -> str (response)
    #   LLM.response(response) -> bool (done) # send response to LLM and get if done
    #   if done: break
    return 0

if __name__ == "__main__":
    main()