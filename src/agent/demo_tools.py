from langchain_openai import ChatOpenAI
from toolkit import create_react_agent_with_tools, duck_search, calculator, InMemorySaver
from src.llm.client import get_llm, get_embeddings

tools = [duck_search, calculator]
llm = get_llm(temperature=0)

agent = create_react_agent_with_tools(llm, tools)
config = {"configurable": {"thread_id": "demo"}}  # memory key

# run
for chunk in agent.stream({"messages": [("user", "How many days until Christmas?")]}, config):
    print(chunk, end="")