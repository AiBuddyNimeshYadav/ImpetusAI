"""
HR Service — Manages HR policy Q&A and document operations.
"""

from ai.agents.hr_policy import answer_hr_query


async def query_hr_policy(
    question: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Answer an HR policy question using the RAG pipeline.

    Returns: {"response_text": str, "sources": list[str]}
    """
    return await answer_hr_query(question, conversation_history)
