from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.chatbot_logic import ChatbotLogic
from backend.neo4j_handle import Neo4jHandler
from backend.openai_handler import OpenAIHandler
from backend.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request format
class MessageRequest(BaseModel):
    message: str

# Response format
class MessageResponse(BaseModel):
    reply: str

# Khởi tạo các handler
neo4j_h = Neo4jHandler(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
openai_h = OpenAIHandler()  # Đổi tên biến cho rõ ràng
chatbot = ChatbotLogic(neo4j_h, openai_h)  # Truyền OpenAIHandler vào

# Endpoint chính
@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(req: MessageRequest):
    user_message = req.message
    reply = chatbot.chat(user_message)
    return {"reply": reply}
