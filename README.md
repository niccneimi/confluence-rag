# Confl-RAG

Корпоративный RAG-ассистент для Confluence базы знаний.

## Структура

- `notebooks/` — ipynb файлы
  - `gpu_ingestion.ipynb` — эмбеддинги на gpu
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

1. Создайте файл .env:
```bash
LLMOPS_API_KEY=
LLMOPS_BASE_URL=
ATLASSIAN_URL=
ATLASSIAN_USERNAME=
ATLASSIAN_PAT=
QDRANT_HOST=
QDRANT_PORT=
QDRANT_KEY=
```
2. Запустите qdrant: `docker compose up -d --build`

3. Экспорт страниц: `python -m src.export`
4. Индексация: `python -m src.ingestion`
5. Вопросы: `python -m src.llm`

## Технологии
- Qdrant (векторная БД)
- BGE-M3 (эмбеддинги)
- LangChain + OpenAI-совместимый API
