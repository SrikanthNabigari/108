"""
108 Embedding Service

Generates vector embeddings for semantic memory search.
Supports multiple providers: OpenAI, Anthropic Voyage, and local models.
"""
import os
import logging
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI text-embedding-3-small embeddings."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._dimension = 1536
        self._client = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required. Install with: uv pip install openai")
        return self._client

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        client = self._get_client()
        response = await client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        client = self._get_client()
        response = await client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


class VoyageEmbeddings(EmbeddingProvider):
    """Anthropic Voyage embeddings (voyage-3)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "voyage-3"):
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.model = model
        self._dimension = 1024
        self._client = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self):
        if self._client is None:
            try:
                import voyageai
                self._client = voyageai.AsyncClient(api_key=self.api_key)
            except ImportError:
                raise ImportError("voyageai package required. Install with: uv pip install voyageai")
        return self._client

    async def embed(self, text: str) -> List[float]:
        """Generate embedding using Voyage."""
        client = self._get_client()
        result = await client.embed([text], model=self.model)
        return result.embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        client = self._get_client()
        result = await client.embed(texts, model=self.model)
        return result.embeddings


class LocalEmbeddings(EmbeddingProvider):
    """
    Local sentence-transformers embeddings.
    Uses all-MiniLM-L6-v2 by default (384 dimensions).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # all-MiniLM-L6-v2

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers required. Install with: "
                    "uv pip install sentence-transformers"
                )
        return self._model

    async def embed(self, text: str) -> List[float]:
        """Generate embedding locally."""
        model = self._get_model()
        embedding = model.encode(text)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        model = self._get_model()
        embeddings = model.encode(texts)
        return [emb.tolist() for emb in embeddings]


class MockEmbeddings(EmbeddingProvider):
    """Mock embeddings for testing (returns random vectors)."""

    def __init__(self, dimension: int = 1536):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> List[float]:
        """Generate deterministic mock embedding based on text hash."""
        import hashlib
        # Create deterministic embedding from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)

        import random
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(self._dimension)]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple texts."""
        return [await self.embed(text) for text in texts]


class EmbeddingService:
    """
    Unified embedding service for 108.

    Auto-selects provider based on available API keys:
    1. OpenAI (if OPENAI_API_KEY set)
    2. Voyage (if VOYAGE_API_KEY set)
    3. Local sentence-transformers (fallback)
    4. Mock embeddings (for testing)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        use_mock: bool = False
    ):
        """
        Initialize embedding service.

        Args:
            provider: Force specific provider ('openai', 'voyage', 'local', 'mock')
            api_key: API key for cloud providers
            use_mock: Use mock embeddings (for testing)
        """
        self._provider: Optional[EmbeddingProvider] = None

        if use_mock:
            self._provider = MockEmbeddings()
            logger.info("Using mock embeddings")
        elif provider == "openai" or (provider is None and os.getenv("OPENAI_API_KEY")):
            self._provider = OpenAIEmbeddings(api_key=api_key)
            logger.info("Using OpenAI embeddings")
        elif provider == "voyage" or (provider is None and os.getenv("VOYAGE_API_KEY")):
            self._provider = VoyageEmbeddings(api_key=api_key)
            logger.info("Using Voyage embeddings")
        elif provider == "local":
            self._provider = LocalEmbeddings()
            logger.info("Using local sentence-transformers embeddings")
        else:
            # Default to mock for development
            self._provider = MockEmbeddings()
            logger.warning("No embedding API key found, using mock embeddings")

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._provider.dimension

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return self._provider.__class__.__name__

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return await self._provider.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return await self._provider.embed_batch(texts)

    async def embed_for_search(self, query: str) -> List[float]:
        """
        Generate embedding optimized for search queries.
        Some providers have different modes for queries vs documents.
        """
        # For now, same as regular embed
        # Could add query-specific prefixes for some models
        return await self.embed(query)


# Singleton for easy access
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    provider: Optional[str] = None,
    use_mock: bool = False
) -> EmbeddingService:
    """
    Get or create the embedding service singleton.

    Args:
        provider: Force specific provider
        use_mock: Use mock embeddings

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(provider=provider, use_mock=use_mock)
    return _embedding_service


def reset_embedding_service():
    """Reset the embedding service singleton (for testing)."""
    global _embedding_service
    _embedding_service = None
