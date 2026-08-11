import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, SparseVectorParams
import uuid
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import HTMLSemanticPreservingSplitter
from typing import List
from src.config import QDRANT_HOST, QDRANT_PORT, QDRANT_KEY, ATLASSIAN_URL
import pickle

class ConfluenceChunkEmbedder:
    def __init__(self, embedding_model_path = './bge-m3-model'):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name = embedding_model_path,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={"normalize_embeddings": True}
        )

    def embed_chunks(self, chunks: List):
        texts = [chunk.page_content for chunk in chunks]
        return self.embedding_model.embed_documents(texts)

class ConfluenceChunker:
    def __init__(self):
        headers_to_split_on = [
            ("h2", "header 2"),
            ('tr', 'table_row')
        ]
        self.text_splitter = HTMLSemanticPreservingSplitter(
            headers_to_split_on=headers_to_split_on,
            elements_to_preserve=["table", "ul", "ol", "code"]
        )

    def basic_chunk(self, html_content):
        chunks = self.text_splitter.split_text(html_content)

        no_duplicate_chunks = []
        for chunk in chunks:
            if chunk.page_content not in chunk.metadata.values():
                chunk.page_content = f"{chunk.metadata.get('header 2', '')}\n{chunk.page_content}"
                no_duplicate_chunks.append(chunk)
        return no_duplicate_chunks

class ConfluenceQdrantClient:
    def __init__(self, collection_name='confluence_pages', reload_vectore_store=False):
        self.collection_name = collection_name

        self.original_qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_KEY)
        
        if reload_vectore_store:
            if self.original_qdrant_client.collection_exists(collection_name=self.collection_name):
                self.original_qdrant_client.delete_collection(collection_name=self.collection_name)
            self.original_qdrant_client.create_collection(
                collection_name = self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )

    def add_embeddings(self, embeddings, chunks, confluence_json_path, page_metadata):
        points = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = uuid.uuid4().hex
            payload = chunk.metadata
            payload['content'] = chunk.page_content
            payload['file_name'] = confluence_json_path
            payload['page_link'] = f"{ATLASSIAN_URL}{page_metadata['page_link']}"
            payload['page_id'] = page_metadata['page_id']
             
            points.append(
                PointStruct(
                    id=chunk_id,
                    vector=embeddings[i],
                    payload=payload
                )
            )

        self.original_qdrant_client.upsert(
            collection_name=self.collection_name,
            wait=False,
            points=points
        )

        print(f"Добавлено {len(points)} чанков в коллекцию '{self.collection_name}' из файла {confluence_json_path}")
        return points

    def __del__(self):
        try:
            if hasattr(self, 'original_qdrant_client') and self.original_qdrant_client is not None:
                self.original_qdrant_client.close()
        except:
            pass    

def run_ingestion(load_from_pkl=False):
    total_points = 0

    if load_from_pkl:
        with open('data/processed/embeddings_data_full.pkl', 'rb') as f:
            all_data = pickle.load(f)
        for filename, data in all_data.items():
            chunks = data['chunks']
            if not chunks:
                continue
            embeddings = data['embeddings']
            page_metadata = data['page_metadata']

            points = qdrant_client.add_embeddings(chunks=chunks, embeddings=embeddings, confluence_json_path=filename,page_metadata=page_metadata)
            total_points += len(points)

    else:      
        for confluence_json_path in os.listdir('data/raw/QA'):
            if confluence_json_path.endswith('.json'):

                with open (f'data/raw/QA/{confluence_json_path}', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    html_content = data['body']['view']['value']

                chunks = chunker.basic_chunk(html_content)
                if not chunks:
                    continue
                embeddings = embedder.embed_chunks(chunks)
                page_metadata = {}
                page_metadata['page_link'] = data['_links']['webui']
                page_metadata['page_id'] = data['id']

                points = qdrant_client.add_embeddings(chunks=chunks, embeddings=embeddings, confluence_json_path=confluence_json_path, page_metadata=page_metadata)
                total_points += len(points)

    print(f"✅ Добавлено {total_points} документов")
    

embedder = ConfluenceChunkEmbedder()
qdrant_client = ConfluenceQdrantClient()
chunker = ConfluenceChunker()

if __name__ == "__main__":
    qdrant_client = ConfluenceQdrantClient(reload_vectore_store=True)

    run_ingestion(load_from_pkl=True)
    