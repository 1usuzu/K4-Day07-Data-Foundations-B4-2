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

    NO_CONTEXT_MESSAGE = "Không tìm thấy thông tin liên quan trong cơ sở tri thức."

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return self.NO_CONTEXT_MESSAGE

        prompt = self._build_prompt(question, results)
        return self.llm_fn(prompt)

    def _build_prompt(self, question: str, results: list[dict]) -> str:
        """Ghép các chunk truy xuất được thành ngữ cảnh có đánh số để dễ truy vết nguồn."""
        context_blocks = []
        for position, result in enumerate(results, start=1):
            source = result["metadata"].get("source_url") or result["metadata"].get("source") or result["id"]
            context_blocks.append(
                f"[{position}] (nguồn: {source} | score: {result['score']:.3f})\n{result['content']}"
            )
        context = "\n\n".join(context_blocks)

        return (
            "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.\n"
            "Chỉ dùng thông tin trong NGỮ CẢNH. Nếu ngữ cảnh không đủ, hãy nói rõ là không biết.\n"
            "Trích dẫn số hiệu đoạn ngữ cảnh ([1], [2], ...) cho các thông tin bạn dùng.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )
