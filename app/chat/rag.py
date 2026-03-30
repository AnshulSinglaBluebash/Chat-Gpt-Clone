import logging
from typing import Sequence

from sqlalchemy.orm import Session

from app.chat.service import get_embedding_client
from app.db.models import Embedding


logger = logging.getLogger(__name__)

DEFAULT_KNOWLEDGE_BASE: Sequence[tuple[str, str]] = (
    (
        "Python",
        "Python is a high-level programming language known for readability, rapid development, and a large ecosystem for web, data, automation, and AI projects.",
    ),
    (
        "FastAPI",
        "FastAPI is a modern Python web framework for building APIs with automatic validation, async support, and interactive Swagger documentation.",
    ),
    (
        "PostgreSQL",
        "PostgreSQL is an open-source relational database that supports SQL, JSON, extensions like pgvector, indexing, and production-ready data integrity features.",
    ),
    (
        "Streamlit",
        "Streamlit helps build Python-based data apps and chat interfaces quickly with simple components like forms, buttons, session state, and chat widgets.",
    ),
    (
        "pgvector",
        "pgvector adds vector storage and similarity search to PostgreSQL, allowing embeddings to be stored in a database table and queried by cosine distance.",
    ),
)


def create_embedding(text: str) -> list[float]:
    client = get_embedding_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def seed_default_embeddings(db: Session) -> None:
    existing = db.query(Embedding.id).first()
    if existing:
        return

    logger.info("Seeding default knowledge base embeddings")
    for topic, content in DEFAULT_KNOWLEDGE_BASE:
        db.add(
            Embedding(
                topic=topic,
                content=content,
                embedding=create_embedding(content),
            )
        )

    db.commit()


def get_relevant_context(db: Session, query: str, limit: int = 3) -> list[str]:
    seed_default_embeddings(db)
    query_embedding = create_embedding(query)

    results = (
        db.query(Embedding)
        .order_by(Embedding.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all()
    )
    return [item.content for item in results if item.content]
