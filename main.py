from langchain_openai import ChatOpenAI

from src.core.config import get_llm


# llm = ChatOpenAI(
#     model="gemini-2.0-flash",             # Any Gemini model
#     api_key="AIzaSyD_H9ASnR8TNyfy8qj7uCVGXU-BfYzxYGs",        # The Gemini API key
#     base_url="https://generativelanguage.googleapis.com/v1beta/"  
# )

llm=get_llm()
response = llm.invoke("Explain quantum computing simply.")
# response = llm.invoke("Explain quantum computing simply.")
print(response.content)