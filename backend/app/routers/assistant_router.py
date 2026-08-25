"""
AI Decision Support Assistant Router.
Provides conversational AI answering urban intelligence and incident queries.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.decision_assistant import decision_assistant
from typing import Dict, Any

router = APIRouter(prefix="/api/assistant", tags=["AI Decision Support"])

class AssistantQueryIn(BaseModel):
    prompt: str

@router.post("/query")
async def ask_assistant(query: AssistantQueryIn) -> Dict[str, Any]:
    """Answers plain-English questions regarding city defects, police incidents, and transit delays."""
    return decision_assistant.query(query.prompt)
