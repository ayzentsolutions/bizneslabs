from app.rag.embeddings import EmbeddingProvider, DeterministicEmbeddingProvider

class ProviderFactory:
    @staticmethod
    def embeddings() -> EmbeddingProvider:
        # Keeps provider selection behind one seam. A production deployment can
        # select a hosted or local embedding model using environment configuration.
        return DeterministicEmbeddingProvider()
