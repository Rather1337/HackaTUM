import subprocess

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
        doc_content = file.read()

    commands = documentation_to_list(doc_content)

    if run_procedure(commands):
        print("Succesfully completed procedure.")
    else:
        print(f"Procedure failed after {num_retries} retries.")

    return 0
