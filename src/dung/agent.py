from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # 1. Retrieve top-k relevant chunks from the store
        results = self.store.search(question, top_k=top_k)
        
        # 2. Build a prompt with the chunks as context
        contexts = []
        for index, res in enumerate(results, start=1):
            source = res["metadata"].get("source", "Unknown")
            contexts.append(f"[Nguồn: {source}]\n{res['content']}")
            
        context_str = "\n\n".join(contexts)
        
        prompt = (
            "Dựa vào các thông tin được cung cấp dưới đây, hãy trả lời câu hỏi.\n"
            "Nếu thông tin không đủ để trả lời, hãy nói rằng bạn không biết.\n\n"
            f"--- Bối cảnh ---\n{context_str}\n\n"
            f"--- Câu hỏi ---\n{question}\n\n"
            "Câu trả lời:"
        )
        
        # 3. Call the LLM to generate an answer
        return self.llm_fn(prompt)
