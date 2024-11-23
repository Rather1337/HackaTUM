import tkinter as tk
from tkinter import filedialog, messagebox
from langchain.tools import tool
import subprocess
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Union
from typing import Literal
from langgraph.graph import END
from langgraph.graph import StateGraph, START

import os
os.environ["OPENAI_API_KEY"] = "#"


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""

    response: str

class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    
shell = subprocess.Popen("/bin/bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

@tool
def terminal(command: str) -> str:
    """Executes the given command in a terminal and returns the output.
    
    Parameters
    ----------
    command : str
        The command that gets executed in the terminal

    Returns
    -------
    str
        the return code of the terminal, 0 means successful execution
    """
    
    print(f"\nExecuting command: {command}")
    debug_label.config(text=f"\nExecuting command: {command}")
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
        
        # print(shell.stdout,shell.stderr)
        if line.startswith("0") or line.startswith("1") or line== (''):
            break

    debug_label.config(text="".join(stdout_lines))
    print("".join(stdout_lines))

    return "".join(stdout_lines)


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan: {plan_str}\n\nYou are tasked with executing step {1}, {task}\n \n Report the status of the execution."""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )

    print(f"Agent response: {agent_response['messages']} \n")

    # for chunk in agent_response['messages']:
    #     print(chunk)


    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    print(f"Replanner: {output}")
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"


async def run_agent(input, result_label):
    tools = [terminal]

    # Choose the LLM that will drive the agent
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent_executor = create_react_agent(llm, tools)

    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """For the given task, create a simple, step-by-step execution plan for an AI agent executing terminal commands. \
                    Each step should correspond to a specific command or action derived from the task that can be solved within the terminal. Ensure that each step is self-contained, \
                    with all necessary details provided for successful execution. Avoid adding unnecessary steps or overly verbose descriptions. Opening or closing the terminal should not be part of this list.\
                    The result of the final step should fulfill the objective outlined in the prompt. Ensure clarity and correctness to prevent missteps.""",
            ),
            ("placeholder", "{messages}"),
        ]
    )
    planner = planner_prompt | ChatOpenAI(
        model="gpt-4o", temperature=0
    ).with_structured_output(Plan)

    replanner_prompt = ChatPromptTemplate.from_template(
        """For the given tutorial or guide, update the step-by-step execution plan based on progress made so far. \
    Each step should represent a specific command or action still required to complete the objective. Ensure that each step is self-contained, \
    clear, and provides all necessary details for successful execution. Avoid repeating already completed steps or adding unnecessary ones.

    Your objective was this:
    {input}

    Your original plan was this:
    {plan}

    You have currently completed the following steps:
    {past_steps}

    Update the plan accordingly. If no further steps are needed and the objective is complete, indicate that. Otherwise, provide the remaining steps that still NEED to be done."""
    )


    replanner = replanner_prompt | ChatOpenAI(
        model="gpt-4o", temperature=0
    ).with_structured_output(Act)


    workflow = StateGraph(PlanExecute)

    # Add the plan node
    workflow.add_node("planner", plan_step)

    # Add the execution step
    workflow.add_node("agent", execute_step)

    # Add a replan node
    workflow.add_node("replan", replan_step)

    workflow.add_edge(START, "planner")

    # From plan we go to agent
    workflow.add_edge("planner", "agent")

    # From agent, we replan
    workflow.add_edge("agent", "replan")

    workflow.add_conditional_edges(
        "replan",
        # Next, we pass in the function that will determine which node is called next.
        should_end,
        ["agent", END],
    )

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable
    app = workflow.compile()

    config = {"recursion_limit": 50}
    async for event in app.astream(input, config=config):
        for k, v in event.items():
            if k != "__end__":
                result_label.config(text=v)

# Define the function to be executed when the "Run" button is clicked
def execute_function():
    file_path = file_path_label.cget("text")
    if file_path == "No file selected":
        result_label.config(text="Please upload a file.")
        return

    try:
        # Example logic: Read file content and display its length
        with open(file_path, 'r') as file:
            content = file.read()

        import asyncio
        asyncio.run(run_agent(content, result_label))
        

    except Exception as e:
        result_label.config(text=f"Error: {e}")

# Define the function to handle file upload
def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_label.config(text=file_path)
    else:
        file_path_label.config(text="No file selected")

# Create the main window
root = tk.Tk()
root.title("File Upload UI Example")
root.geometry("500x300")

# Create and place a label for instructions
instruction_label = tk.Label(root, text="Upload a file and click 'Run':", font=("Arial", 12))
instruction_label.pack(pady=10)

# Create and place a button to upload files
upload_button = tk.Button(root, text="Upload File", font=("Arial", 12), command=upload_file)
upload_button.pack(pady=5)

# Create and place a label to display the selected file path
file_path_label = tk.Label(root, text="No file selected", font=("Arial", 10), fg="gray")
file_path_label.pack(pady=5)

# Create and place a "Run" button
run_button = tk.Button(root, text="Run", font=("Arial", 12), command=execute_function)
run_button.pack(pady=10)

# Create and place a label to display results
result_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
result_label.pack(pady=10)

# Create and place a label to display results
debug_label = tk.Label(root, text="", font=("Arial", 12), fg="black")
debug_label.pack(pady=10)

# Run the main event loop
root.mainloop()