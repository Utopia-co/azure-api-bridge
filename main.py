from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.schemas import UserInput
from app.manager import ChatManager

app = FastAPI(title="Azure OpenAI Threaded Runner API", version="1.0.0")

# Instanciamos o manager uma única vez para reuso
chat_manager = ChatManager()

@app.post("/chat/stream")
def chat_stream(input_data: UserInput):
    # Usa o manager para obter a resposta em streaming
    response_stream = chat_manager.get_streaming_response(
        assistant_id=input_data.assistant_id,
        message=input_data.message
    )
    return StreamingResponse(response_stream, media_type="text/plain")
