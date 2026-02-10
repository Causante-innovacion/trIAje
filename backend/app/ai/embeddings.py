"""
Embeddings Service
Servicio unificado para generación de embeddings.
Soporta OpenAI y modelos locales (sentence-transformers).
"""

from abc import ABC, abstractmethod
from enum import Enum


class EmbeddingProvider(str, Enum):
    """Proveedores de embeddings disponibles"""
    OPENAI = "openai"
    LOCAL = "local"  # sentence-transformers


class EmbeddingService(ABC):
    """Interfaz abstracta para servicios de embeddings"""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Genera embedding para un texto"""
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para múltiples textos"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensión del vector de embedding"""
        pass


class OpenAIEmbeddingService(EmbeddingService):
    """Servicio de embeddings usando OpenAI"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
    ):
        from app.core.config import settings

        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self._client = None

        # Dimensiones por modelo
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

    @property
    def dimension(self) -> int:
        return self._dimensions.get(self.model, 1536)

    async def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def embed_text(self, text: str) -> list[float]:
        """Genera embedding para un texto"""
        client = await self._get_client()
        response = await client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para múltiples textos (batch)"""
        if not texts:
            return []

        client = await self._get_client()

        # OpenAI permite hasta 2048 textos por request
        batch_size = 2048
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await client.embeddings.create(
                model=self.model,
                input=batch,
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings


class LocalEmbeddingService(EmbeddingService):
    """
    Servicio de embeddings usando modelos locales (sentence-transformers).
    Útil para desarrollo sin costos de API.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 768  # Default para mpnet-base-v2

        # Dimensiones conocidas
        self._known_dimensions = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "paraphrase-multilingual-MiniLM-L12-v2": 384,
            "paraphrase-multilingual-mpnet-base-v2": 768,
        }

    @property
    def dimension(self) -> int:
        return self._known_dimensions.get(self.model_name, self._dimension)

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers no instalado. "
                    "Instalar con: pip install sentence-transformers"
                )
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """Genera embedding para un texto"""
        model = self._load_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para múltiples textos"""
        if not texts:
            return []

        model = self._load_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class EmbeddingServiceFactory:
    """Factory para crear el servicio de embeddings según configuración"""

    _instance: EmbeddingService | None = None

    @classmethod
    def get_service(
        cls,
        provider: EmbeddingProvider = EmbeddingProvider.OPENAI,
        **kwargs,
    ) -> EmbeddingService:
        """
        Obtiene el servicio de embeddings.

        Args:
            provider: Proveedor a usar (openai, local)
            **kwargs: Argumentos adicionales según proveedor

        Returns:
            EmbeddingService configurado
        """
        if provider == EmbeddingProvider.OPENAI:
            return OpenAIEmbeddingService(**kwargs)
        elif provider == EmbeddingProvider.LOCAL:
            return LocalEmbeddingService(**kwargs)
        else:
            raise ValueError(f"Proveedor desconocido: {provider}")

    @classmethod
    def get_default_service(cls) -> EmbeddingService:
        """Obtiene servicio con configuración por defecto"""
        if cls._instance is None:
            from app.core.config import settings

            provider = getattr(settings, "EMBEDDING_PROVIDER", "openai")

            if provider == "local":
                model_name = getattr(
                    settings,
                    "EMBEDDING_LOCAL_MODEL",
                    "paraphrase-multilingual-mpnet-base-v2",
                )
                cls._instance = LocalEmbeddingService(model_name=model_name)
            elif hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
                cls._instance = OpenAIEmbeddingService()
            else:
                cls._instance = LocalEmbeddingService()

        return cls._instance


# Función de conveniencia
async def embed_text(text: str) -> list[float]:
    """Genera embedding usando el servicio por defecto"""
    service = EmbeddingServiceFactory.get_default_service()
    return await service.embed_text(text)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Genera embeddings usando el servicio por defecto"""
    service = EmbeddingServiceFactory.get_default_service()
    return await service.embed_texts(texts)
