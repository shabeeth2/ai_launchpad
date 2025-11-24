import asyncio
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.llm.client import get_llm, get_embeddings
from src.llm.config import settings

async def main():
    print(f"--- Testing  ---")
    print(f"Target: {settings.BASE_URL}")

    # 1. Test LLM
    print("\n1. Testing LLM Connection...")
    llm = get_llm(temperature=0.7)
    try:
        # ainvoke is the Async method
        response = await llm.ainvoke("what is   Operational' and nothing else.")
        print(f"✅ LLM Response: {response.content}")
    except Exception as e:
        print(f"❌ LLM Failed: {e}")

    # 2. Test Embeddings
    print("\n2. Testing Embeddings...")
    embed_model = get_embeddings()
    try:
        vector = await embed_model.aembed_query("Hello World")
        print(f"✅ Embedding Generated. Dimensions: {len(vector)}")
    except Exception as e:
        print(f"❌ Embeddings Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())