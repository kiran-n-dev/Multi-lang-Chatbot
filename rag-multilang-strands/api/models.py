
# api/models.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    userLang: Optional[str] = "en"

class TableBlock(BaseModel):
    html: str
    title: Optional[str] = None

class ImageBlock(BaseModel):
    src: str
    caption: Optional[str] = None
    alt: Optional[str] = None

class ChatResponse(BaseModel):
       text: str
       tables: List[TableBlock] = []
