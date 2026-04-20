import logging
from ai.llm.gateway import get_llm_gateway
from ai.rag.retriever import get_rag_service

logger = logging.getLogger(__name__)

async def answer_hr_query(user_query: str, history: list[dict] = None) -> dict:
    rag = get_rag_service()
    llm = get_llm_gateway()
    try:
        results = rag.search(user_query, collection_name="hr_policies", top_k=3)
        context = ""
        sources = []
        for res in results:
            raw = res.get('metadata', {}).get('source', 'Unknown')
            clean = raw.replace('_', ' ').replace('.md', '').replace('.pdf', '').title()
            if raw not in sources:
                sources.append(raw)
            context += f"[{clean}]:\n{res.get('content', '')}\n\n"

        prompt = f"Answer the user query based ONLY on the context below. If the answer is not in the context, say so. Cite sources by their name shown in brackets.\n\nContext:\n{context}\n\nQuery: {user_query}"
        
        messages = [{"role": "system", "content": "You are a helpful HR Assistant. Answer precisely based on provided policy context."}]
        if history:
            messages.extend(history[-3:])
        messages.append({"role": "user", "content": prompt})

        llm_response = await llm.generate_with_history(messages)
        return {
            "response_text": llm_response.content,
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Error in HR policy agent: {type(e).__name__}: {e}")
        return {
            "response_text": "I encountered an error while searching the HR knowledge base.",
            "sources": []
        }
