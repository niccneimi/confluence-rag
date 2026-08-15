from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.config import LLMOPS_API_KEY, LLMOPS_BASE_URL
from src.retrieval import qdrant_tool
import asyncio

chat_model = ChatOpenAI(
    model = 'qwen3-coder-next',
    api_key = LLMOPS_API_KEY,
    base_url = LLMOPS_BASE_URL,
    temperature = 0.3,
    max_completion_tokens=8192,
    streaming=True
)

agent = create_agent(
    model = chat_model,
    tools = [qdrant_tool],
    system_prompt = (
        "Ты ассистент по Confluence. Для любых вопросов сначала вызывай qdrant_tool, "
        "затем давай точный и подробный ответ на основе найденных данных. "
        "Если данных нет — ответь: 'данных нет'. "
        "Всегда указывай ссылки на Confluence-страницы по каждому факту. "
        "Дополняй запрос пользователя ключевыми словами для точного поиска."
    )
)

async def main():
    content = """Что такое UMS"""

    with open('llm_answer.md', 'w') as file:
        agent_stream = agent.astream_events({
            "messages": [{'role': 'user', 'content': content}]
        })
        async for event in agent_stream:
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # print(chunk.content, end="", flush=True)
                    file.write(chunk.content)
                    file.flush()

if __name__ == '__main__':
    asyncio.run(main())

