from langchain.tools import BaseTool
from typing import Optional, Any
from src.ingestion import qdrant_client, embedder

from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

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
    
    def _run(self, query: str, top_k: int = 5) -> str:
        try:
            query_vector = self.embedder.embed_query(query)
            
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                with_payload=True,
                limit=top_k * 10,
            ).points
            
            if not search_results:
                return "По вашему запросу ничего не найдено."
            
            search_results = self._rerank(query, search_results, top_k)

            formatted_results = []
            for i, result in enumerate(search_results, 1):
                content = result.payload.get('content', '')
                header = result.payload.get('header 2', 'Без заголовка')
                page_link = result.payload.get('page_link', 'Нет ссылки')
                formatted_results.append(
                    f"Результат {i}\n"
                    f"Заголовок: {header}\n"
                    f"Ссылка: {page_link}\n" 
                    f"Содержание: {content}"
                )
            
            return "\n\n---\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Произошла ошибка при поиске: {str(e)}"

    def _rerank(self, query: str, search_results: list[str], top_k: int = 5) -> list[str]:
        reranked = {}
        pairs = [[query, search_result.payload.get('content', '')] for search_result in search_results]
        with torch.no_grad():
            inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors="pt", max_length=512)
            scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
        for i, score in enumerate(scores):
            reranked[i] = score.item()

        sorted_results = dict(sorted(reranked.items(), key=lambda x: x[1], reverse=True))
        rerank_result = [search_results[idx] for idx in sorted_results.keys()]
        return rerank_result[:top_k]
    
    async def _arun(self, query: str, top_k: int = 5) -> str:
        return self._run(query, top_k)

qdrant_tool = QdrantSearchTool(
    qdrant_client=qdrant_client.original_qdrant_client,
    embedder=embedder.embedding_model,
    collection_name='confluence_pages'
)

model_name = 'BAAI/bge-reranker-base'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
