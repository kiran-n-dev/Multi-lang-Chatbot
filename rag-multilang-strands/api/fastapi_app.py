
# api/fastapi_app.py
from fastapi import FastAPI
from api.routes.chat import router as chat_router
from api.routes.upload import router as upload_router

app = FastAPI(title="RAG Multilang Chatbot API")
app.include_router(upload_router, prefix="/api")
app.include_router(chat_router,  prefix="/api")

