from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Khởi tạo chromadb client + collection
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": doc.metadata,
            "embedding": embedding
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)
        results = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            results.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score
            })
        
        # Sắp xếp kết quả theo điểm số giảm dần
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.
        """
        if self._use_chroma and self._collection is not None:
            ids = [doc.id for doc in docs]
            documents = [doc.content for doc in docs]
            metadatas = [doc.metadata for doc in docs]
            embeddings = [self._embedding_fn(doc.content) for doc in docs]
            self._collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        else:
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding], 
                n_results=top_k
            )
            
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    # Chroma return khoảng cách (distance), có thể cần xử lý nếu cần score tương tự dot product
                    score = results["distances"][0][i] if results["distances"] else 0.0
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": score
                    })
            return formatted_results
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding], 
                n_results=top_k, 
                where=metadata_filter if metadata_filter else None
            )
            
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": results["distances"][0][i] if results["distances"] else 0.0
                    })
            return formatted_results
        else:
            if metadata_filter is None:
                metadata_filter = {}
                
            filtered_records = []
            for record in self._store:
                match = True
                for k, v in metadata_filter.items():
                    if record["metadata"].get(k) != v:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
                    
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.
        """
        if self._use_chroma and self._collection is not None:
            initial_count = self._collection.count()
            # In chroma we can delete by ids or where. The test uses id="doc_to_delete" with no metadata.
            # So we try both.
            self._collection.delete(ids=[doc_id])
            self._collection.delete(where={"doc_id": doc_id})
            return self._collection.count() < initial_count
        else:
            initial_len = len(self._store)
            self._store = [
                record for record in self._store
                if record["id"] != doc_id and record["metadata"].get("doc_id") != doc_id
            ]
            return len(self._store) < initial_len
