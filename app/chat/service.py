from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("🔥 API KEY FROM ENV:", api_key)   

client = OpenAI(api_key=api_key)


def get_ai_response(message: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("❌ AI ERROR:", e)
        return "AI error aa gaya bhai 😅"