from typing import Generator
from .azure_service import AzureThreadedAssistantRunner

class ChatManager:
    def __init__(self):
        # Aqui poderíamos ter logs, conexões com BD, cache, etc.
        pass

    def get_streaming_response(self, assistant_id: str, message: str) -> Generator[str, None, None]:
        # Instancia o runner com o assistant_id informado
        runner = AzureThreadedAssistantRunner(assistant_id=assistant_id)

        # Retorna o streaming final
        return runner.stream_azure_response(user_input=message)
