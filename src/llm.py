from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.config import LLMOPS_API_KEY, LLMOPS_BASE_URL
from src.retrieval import qdrant_tool

chat_model = ChatOpenAI(
    model = 'qwen3-coder-next',
    api_key = LLMOPS_API_KEY,
    base_url = LLMOPS_BASE_URL,
    temperature = 0.3
)

agent = create_agent(
    model = chat_model,
    tools = [qdrant_tool],
    system_prompt=(
        "Ты полезный ассистент. Для вопросов по базе данных по Confluence"
        "Сначала вызови qdrant_tool, затем ответь корректно"
    )
)

if __name__ == '__main__':
    result = agent.invoke({
        "messages": [{'role': 'user', 'content': 'какие автотеты посоветуешь описать по сократителю ссылок?'}]
    })

    print(result)
    print(result['messages'][-1].content)