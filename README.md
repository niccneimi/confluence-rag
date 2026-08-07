# Confl-RAG

Корпоративный RAG-ассистент для Confluence базы знаний.

## Структура

- `src/` — исходный код
  - `config.py` — конфигурация (API ключи, Confluence)
  - `export.py` — экспорт страниц из Confluence
  - `ingestion.py` — чанкинг, эмбеддинги, загрузка в Qdrant
  - `retrieval.py` — RAG-поиск через Qdrant
  - `llm.py` — агент с интеграцией LLM

- `data/raw/` — JSON файлы экспорта Confluence
- `qdrant_vector_store/` — векторная БД
- `bge-m3-model/` — модель эмбеддингов (BAAI/bge-m3)

## Использование

1. Экспорт страниц: `python -m src.export`
2. Индексация: `python -m src.ingestion`
3. Вопросы: `python -m src.llm`

## Технологии
- Qdrant (векторная БД)
- BGE-M3 (эмбеддинги)
- LangChain + OpenAI-совместимый API
