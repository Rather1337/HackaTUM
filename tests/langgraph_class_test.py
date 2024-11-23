from agent import Agent
from langchain_core.messages import HumanMessage

with open("doc.txt", "r") as f:
    doc_content = f.read()

# llm = LLM(doc_content)

# final_state = llm.app.invoke({"messages": [HumanMessage(content=f"i have this doc: {doc_content}. produce ONLY the commands that I have to put in the terminals as a comma seperated list. do  not give out anything else!")]},
#     config={"configurable": {"thread_id": 42}})


#print(final_state["messages"][-1].content)