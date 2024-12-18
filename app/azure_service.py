import os
import threading
import queue
from typing import Generator
from openai import AzureOpenAI
from openai import AssistantEventHandler
from .db.dynamo import DynamoDBManager

# Runner que interage com o Azure e DynamoDB
class AzureThreadedAssistantRunner:
    def __init__(self, assistant_id: str, table_name: str):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.assistant_id = assistant_id
        self.dynamo_manager = DynamoDBManager(table_name)

    def stream_azure_response(self, conversation_id: str, user_input: str) -> Generator[str, None, None]:
        # Armazena a mensagem do usuário
        self.dynamo_manager.insert_message(
            conversation_id=conversation_id,
            role="user",
            content=user_input
        )

        # Cria uma thread no Azure
        thread = self.client.beta.threads.create()

        # Adiciona a mensagem do usuário ao Azure
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Cria fila para receber os deltas
        q = queue.Queue()

        # Handler para armazenar saídas
        class MyEventHandler(AssistantEventHandler):
            def on_text_delta(self, delta, snapshot):
                if delta.value:
                    q.put(delta.value)
                    self.dynamo_manager.insert_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=delta.value
                    )

        handler = MyEventHandler()

        # Função de streaming
        def run_stream():
            with self.client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                event_handler=handler
            ) as stream:
                stream.until_done()
            q.put(None)  # Sinaliza fim do streaming

        # Inicia o streaming
        t = threading.Thread(target=run_stream, daemon=True)
        t.start()

        # Consome e exibe mensagens
        while True:
            chunk = q.get()
            if chunk is None:
                break
            yield chunk
