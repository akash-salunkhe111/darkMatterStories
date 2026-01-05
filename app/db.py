import uuid
from typing import Any, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from app.settings import settings

class Database:
    def __init__(self):
        # QdrantClient "location" argument handles both URLs and ":memory:"
        self.client = QdrantClient(location=settings.QDRANT_URL)
        # Initialize FastEmbed (downloads model on first run if not present)
        self.embedding_model = TextEmbedding()
        self.collection_name = settings.QDRANT_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Default for fastembed (BAAI/bge-small-en-v1.5)
                    distance=models.Distance.COSINE,
                ),
            )

    def add_story(self, story_text: str, metadata: Dict[str, Any]) -> str:
        # Generate embedding
        # embed returns a generator, we take the first item
        embedding = list(self.embedding_model.embed([story_text]))[0]
        
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={"text": story_text, **metadata}
                )
            ]
        )
        return point_id

# Global instance
db = Database()
