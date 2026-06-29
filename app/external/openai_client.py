"""
OpenAI API 클라이언트 래퍼.
embed_text, summarize_issue_cluster, generate_personalized_briefing 등에서 사용.

TODO(구현 필요):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def create_embedding(text: str) -> list[float]:
        resp = await client.embeddings.create(model=settings.OPENAI_EMBEDDING_MODEL, input=text)
        return resp.data[0].embedding

    async def chat_completion_json(system_prompt: str, user_prompt: str) -> dict:
        resp = await client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        import json
        return json.loads(resp.choices[0].message.content)
"""
from app.core.config import settings


async def create_embedding(text: str) -> list[float]:
    """TODO(구현 필요): 위 docstring 참고"""
    raise NotImplementedError


async def chat_completion_json(system_prompt: str, user_prompt: str) -> dict:
    """TODO(구현 필요): 위 docstring 참고"""
    raise NotImplementedError
