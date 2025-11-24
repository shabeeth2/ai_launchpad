from langchain_openai import ChatOpenAI
from toolkit import create_react_agent_with_tools, duck_search, calculator, InMemorySaver

tools = [duck_search, calculator]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_react_agent_with_tools(llm, tools)
config = {"configurable": {"thread_id": "demo"}}  # memory key

# run
for chunk in agent.stream({"messages": [("user", "How many days until Christmas?")]}, config):
    print(chunk, end="")