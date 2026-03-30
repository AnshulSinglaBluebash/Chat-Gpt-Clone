import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def get_embedding_client() -> OpenAI:
    return OpenAI(api_key=api_key)


def get_ai_response(message: str, context_chunks: list[str] | None = None) -> str:
    client = get_embedding_client()
    context = "\n\n".join(context_chunks or [])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Use the provided context when it is relevant, and be clear when the answer comes from general knowledge."
            ),
        }
    ]

    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Relevant context:\n{context}",
            }
        )

    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return response.choices[0].message.content or "No response returned by the AI model."
    except Exception:
        return "AI error aa gaya bhai 😅"
