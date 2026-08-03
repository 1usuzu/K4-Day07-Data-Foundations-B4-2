# Gemini Embedder Design

## Goal

Replace the project's OpenAI embedding integration with Gemini. The mock and
local embedders remain available and the application continues to fall back to
the mock embedder when an optional backend cannot be created.

## Public interface

- `GeminiEmbedder` replaces `OpenAIEmbedder` in `src.embeddings` and the `src`
  package exports.
- `GEMINI_EMBEDDING_MODEL` replaces `OPENAI_EMBEDDING_MODEL`, with default
  value `gemini-embedding-2`.
- Users select it with `EMBEDDING_PROVIDER=gemini` and configure the official
  SDK through `GEMINI_API_KEY`.
- `GeminiEmbedder(text)` returns `list[float]`, preserving the existing
  embedding-function contract used by `EmbeddingStore`.

## Implementation

`GeminiEmbedder` imports the current official `google-genai` SDK lazily in its
constructor. It creates `genai.Client()` and calls
`client.models.embed_content(model=self.model_name, contents=text)`. The first
result embedding's `values` property is converted to floats.

`main.py` will recognise `gemini` as the remote provider. The local, mock, and
fallback behaviour do not change.

The documentation and optional dependency list will give this smoke test:

```bash
pip install google-genai
export GEMINI_API_KEY=your-key-here
python3 - <<'PY'
from src import GeminiEmbedder
embedder = GeminiEmbedder()
print(embedder._backend_name)
print(len(embedder("embedding smoke test")))
PY
```

## Error handling and tests

Missing SDK, invalid key, or remote API failures are handled by the existing
`main.py` fallback when the Gemini provider is selected. Direct construction of
`GeminiEmbedder` surfaces the SDK/API exception, consistent with the old
OpenAI implementation.

Tests will fake the Gemini SDK module and assert the model request and returned
numeric vector, so no genuine key or network call is required. Existing mock
and store tests must continue to pass.

## Scope

This change removes the OpenAI-specific class, model constant, provider name,
README instructions, and dependency references. It does not change chunking,
vector-store semantics, or the local embedding backend.
