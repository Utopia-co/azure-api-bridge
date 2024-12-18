from openai import AzureOpenAI
import os
import time
from IPython.display import clear_output

class AzureAssistant:
    def __init__(self, assistant_id: str):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-05-01-preview",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.assistant_id = assistant_id

    def create_thread(self):
        return self.client.beta.threads.create()
    
    def add_msg(self, thread_id, content, role='user'):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
    
    def run_thread(self, thread_id, model="gpt-4o"):
        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            model=model
        )
    
    def handler(self, content: str, thread_id=None):

        if not thread_id:
            thread = self.create_thread()
            thread_id = thread.id

        self.add_msg(thread_id=thread_id, content=content)
        run = self.run_thread(thread_id=thread_id)

        start_time = time.time()
        status = run.status

        while status not in ["completed", "cancelled", "expired", "failed"]:
            time.sleep(5)
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id,run_id=run.id)
            print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
            status = run.status
            print(f'Status: {status}')
            clear_output(wait=True)

        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
            )
        return messages.data[0].model_dump_json(indent=2)
    
if __name__ == "__main__":
    client = AzureAssistant("asst_jLLqOWF2RxzMu967s7nQngFs")
    x = client.handler("Explique aprendizado profundo de maneira simples.")
    print(x)
