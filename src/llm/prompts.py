"""
Prompt Templates using LangChain
"""
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPTS = {
    "default": "You are a helpful, harmless, and honest AI assistant.",
    "expert": "You are an expert AI assistant with deep knowledge across multiple domains.",
    "coder": "You are an expert programmer. Write clean, efficient, well-documented code.",
    "analyst": "You are a data analyst AI. Analyze critically and provide insights.",
}


# ============================================================================
# SIMPLE PROMPTS
# ============================================================================

def create_simple_prompt(template: str) -> PromptTemplate:
    """Create a simple prompt template"""
    return PromptTemplate.from_template(template)


# Example usage
SUMMARIZE_PROMPT = create_simple_prompt(
    "Summarize the following text in {style} style:\n\n{text}"
)


# ============================================================================
# CHAT PROMPTS
# ============================================================================

def create_chat_prompt(
    system_message: str,
    human_message: str
) -> ChatPromptTemplate:
    """Create a chat prompt with system and human messages"""
    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", human_message)
    ])


# Task-specific prompts
QA_PROMPT = create_chat_prompt(
    system_message="Answer questions based on the provided context.",
    human_message="Context: {context}\n\nQuestion: {question}"
)

EXTRACT_PROMPT = create_chat_prompt(
    system_message="Extract structured information from text.",
    human_message="Extract: {fields}\n\nText: {text}\n\nReturn JSON."
)

CLASSIFY_PROMPT = create_chat_prompt(
    system_message="Classify text into categories.",
    human_message="Categories: {categories}\n\nText: {text}"
)


# ============================================================================
# AGENT PROMPTS
# ============================================================================

REACT_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI agent that can use tools.

Available tools:
{tools}

To use a tool, respond with JSON:
{{
    "thought": "your reasoning",
    "action": "tool_name",
    "action_input": {{"arg": "value"}}
}}

To answer, respond with:
{{
    "thought": "I have enough information",
    "final_answer": "complete answer"
}}"""),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])


# ============================================================================
# RAG PROMPTS
# ============================================================================

RAG_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Answer questions using the provided context. Cite sources with [1], [2], etc."),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])

CONVERSATIONAL_RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to a knowledge base."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])


# ============================================================================
# CONVERSATION PROMPTS
# ============================================================================

CONVERSATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{system_message}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])


# # Usage Examples
# if __name__ == "__main__":
#     # Simple prompt
#     prompt = SUMMARIZE_PROMPT.format(
#         text="Long article...",
#         style="concise"
#     )
#     print(prompt)
    
#     # Chat prompt
#     messages = QA_PROMPT.format_messages(
#         context="Paris is the capital of France.",
#         question="What is the capital of France?"
#     )
#     print(messages)
    
#     # Agent prompt
#     agent_messages = REACT_AGENT_PROMPT.format_messages(
#         tools="search, calculator",
#         input="What is 25 * 4?",
#         agent_scratchpad=[]
#     )
#     print(agent_messages)