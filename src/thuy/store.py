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
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                collection_name,
                metadata={"hnsw:space": "ip"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_id", doc.id)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []
        query_embedding = self._embedding_fn(query)
        results = []
        for record in records:
            result = {key: value for key, value in record.items() if key != "embedding"}
            result["score"] = _dot(query_embedding, record["embedding"])
            results.append(result)
        return sorted(results, key=lambda record: record["score"], reverse=True)[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        records = [self._make_record(doc) for doc in docs]
        if self._use_chroma and self._collection is not None and records:
            self._collection.add(
                ids=[record["id"] for record in records],
                documents=[record["content"] for record in records],
                metadatas=[record["metadata"] for record in records],
                embeddings=[record["embedding"] for record in records],
            )
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            if top_k <= 0 or self._collection.count() == 0:
                return []
            response = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=min(top_k, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
            return [
                {"id": item_id, "content": content, "metadata": metadata or {}, "score": 1 - distance}
                for item_id, content, metadata, distance in zip(
                    response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]
                )
            ]
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)
        if self._use_chroma and self._collection is not None:
            if top_k <= 0:
                return []
            response = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=min(top_k, self._collection.count()),
                where=metadata_filter,
                include=["documents", "metadatas", "distances"],
            )
            return [
                {"id": item_id, "content": content, "metadata": metadata or {}, "score": 1 - distance}
                for item_id, content, metadata, distance in zip(
                    response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]
                )
            ]
        records = [
            record for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            existing = self._collection.get(where={"doc_id": doc_id}, include=[])
            if not existing["ids"]:
                return False
            self._collection.delete(ids=existing["ids"])
            return True
        before = len(self._store)
        self._store = [record for record in self._store if record["metadata"].get("doc_id") != doc_id]
        return len(self._store) != before
