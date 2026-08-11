from langchain.tools import BaseTool
from typing import Optional, Any
from src.ingestion import qdrant_client, embedder

class QdrantSearchTool(BaseTool):
    name: str = "qdrant_search"
    description: str = """
    Используй этот инструмент для поиска информации в корпоративной базе знаний Confluence.
    Введи поисковый запрос, чтобы найти релевантные документы, инструкции и руководства.
    """
    
    client: Optional[Any] = None
    embedder: Optional[Any] = None
    collection_name: str = "confluence_pages"
    
    def __init__(self, qdrant_client, embedder, collection_name="confluence_pages", **kwargs):
        super().__init__(
            client=qdrant_client,
            embedder=embedder,
            collection_name=collection_name,
            **kwargs
        )
    
    def _run(self, query: str, top_k: int = 100) -> str:
        try:
            query_vector = self.embedder.embed_query(query)
            
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                with_payload=True,
                limit=top_k,
            ).points
            
            if not search_results:
                return "По вашему запросу ничего не найдено."
            
            formatted_results = []
            for i, result in enumerate(search_results, 1):
                content = result.payload.get('content', '')
                header = result.payload.get('header 2', 'Без заголовка')
                page_link = result.payload.get('page_link', 'Нет ссылки')
                formatted_results.append(
                    f"Результат {i} (релевантность: {result.score:.2f}):\n"
                    f"Заголовок: {header}\n"
                    f"Ссылка: {page_link}\n" 
                    f"Содержание: {content}"
                )
            
            return "\n\n---\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Произошла ошибка при поиске: {str(e)}"
    
    async def _arun(self, query: str, top_k: int = 100) -> str:
        return self._run(query, top_k)

qdrant_tool = QdrantSearchTool(
    qdrant_client=qdrant_client.original_qdrant_client,
    embedder=embedder.embedding_model,
    collection_name='confluence_pages'
)