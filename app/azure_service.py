import os
import threading
import queue
from typing import Generator
from openai import AzureOpenAI
from openai import AssistantEventHandler

class MyEventHandler(AssistantEventHandler):
    def __init__(self, q: queue.Queue):
        super().__init__()  # Inicializa a classe base para evitar erros
        self.q = q

    def on_text_delta(self, delta, snapshot):
        if delta.value:
            self.q.put(delta.value)

class AzureThreadedAssistantRunner:
    def __init__(self, assistant_id: str):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.assistant_id = assistant_id

    def stream_azure_response(self, user_input: str) -> Generator[str, None, None]:
        # Cria um novo thread
        thread = self.client.beta.threads.create()

        # Adiciona a mensagem do usuário
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Cria uma fila para receber os deltas
        q = queue.Queue()

        # Cria o event handler para inserir mensagens na fila
        handler = MyEventHandler(q)

        # Função que executa o streaming em uma thread separada
        def run_stream():
            # Não usamos 'stream=True' aqui, pois runs.stream já é streaming
            with self.client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                event_handler=handler
            ) as stream:
                stream.until_done()
            q.put(None)  # Sinaliza fim do streaming

        # Inicia a thread de streaming
        t = threading.Thread(target=run_stream, daemon=True)
        t.start()

        # Consome a fila e retorna via yield
        while True:
            chunk = q.get()
            if chunk is None:
                break
            yield chunk
