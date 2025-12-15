
# api/routes/chat.py
from fastapi import APIRouter
from api.models import ChatRequest, ChatResponse
from agent.strands_agent import answer_with_converse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Get structured answer from Bedrock via Converse
    result = answer_with_converse(req.query, req.userLang or "en")

    # Normalize into DTO
    return ChatResponse(
        text=result.get("text", ""),
        tables=[{"html": t} if isinstance(t, str) else t for t in result.get("tables", [])],
        images=[{"src": i} if isinstance(i, str) else i for i in result.get("images", [])],
    )
