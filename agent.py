from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
import os


class LLM:
    def __init__(self, doc_content: str):
        with open("api_key.txt", "r", encoding="utf-8") as file:
            api_key = file.read()
        os.environ["OPENAI_API_KEY"] = api_key
        self.doc_content = doc_content
        self.tools = [self.search]
        self.tool_node = ToolNode(self.tools)
        self.model = ChatOpenAI(model="gpt-4", temperature=0).bind_tools(self.tools)
        self.workflow = StateGraph(MessagesState)
        self.workflow.add_node("agent", self.call_model)
        self.workflow.add_node("tools", self.tool_node)
        self.workflow.add_edge(START, "agent")
        self.workflow.add_edge("tools", "agent")
        self.workflow.add_conditional_edges("agent", self.should_continue)
        checkpointer = MemorySaver()
        self.app = self.workflow.compile(checkpointer=checkpointer)

    @tool
    def search(self, query: str):
        """Call to surf the web."""
        if "sf" in query.lower() or "san francisco" in query.lower():
            return "It's 60 degrees and foggy."
        return "It's 90 degrees and sunny."

    def should_continue(self, state: MessagesState) -> Literal["tools", END]:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}


class Agent:
    def __init__(self, doc_content: str):
        self.llm = LLM(doc_content)
        self.llm.app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"I have this tutorial of my onboarding process: {doc_content}"
                    )
                ]
            },
            config={"configurable": {"thread_id": 42}}
        )

        self.inital_cmd = True

    def get_next_cmd(self):
        if self.inital_cmd:
            self.inital_cmd = False
            return self.llm.app.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="What is the first command to execute? Return it as single string and nothing else."
                        )
                    ]
                },
                config={"configurable": {"thread_id": 42}},
            )["messages"][-1].content

        else:
            return self.llm.app.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="The previous command executed without problems. From the tutorial, what is the next command to execute? Return it as single string and nothing else. If you are done executing all commands that are necessary to complete the tutorial, return 'done'."
                        )
                    ]
                },
                config={"configurable": {"thread_id": 42}},
            )["messages"][-1].content

    def retry_cmd(self, error_msg: str):
        return self.llm.app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"The previous command failed with the following error: {error_msg}. Give me a new command based on the error message. Return it as single string and nothing else."
                    )
                ]
            },
            config={"configurable": {"thread_id": 42}},
        )["messages"][-1].content
