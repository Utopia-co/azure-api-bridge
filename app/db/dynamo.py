import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

class DynamoDBManager:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.dynamodb = self._configure_dynamodb()
        self.table = self._get_table()

    def _configure_dynamodb(self):
        """
        Configura a conexão com o DynamoDB.
        """
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT", None)
        region_name = os.getenv("AWS_REGION", "us-west-2")
        return boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)

    def _get_table(self):
        """
        Conecta-se a uma tabela existente.
        """
        try:
            return self.dynamodb.Table(self.table_name)
        except ClientError as e:
            print(f"Erro ao acessar a tabela {self.table_name}: {e}")
            raise

    def insert_message(self, conversation_id: str, role: str, content: str):
        """
        Insere ou atualiza uma conversa com a nova mensagem dentro do array 'messages'.
        """
        try:
            # Adiciona a nova mensagem ao array
            new_message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}

            # Atualiza a tabela: adiciona a nova mensagem ao array 'messages'
            response = self.table.update_item(
                Key={'conversation_id': conversation_id},
                UpdateExpression="SET #msgs = list_append(if_not_exists(#msgs, :empty_list), :new_message)",
                ExpressionAttributeNames={"#msgs": "messages"},
                ExpressionAttributeValues={
                    ":new_message": [new_message],
                    ":empty_list": []
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f"Mensagem adicionada à conversa {conversation_id}: {role} - {content}")
            return response
        except ClientError as e:
            print(f"Erro ao atualizar conversa: {e}")
            raise

    def get_conversation(self, conversation_id: str):
        """
        Recupera todas as mensagens de uma conversa específica.
        """
        try:
            response = self.table.get_item(Key={'conversation_id': conversation_id})
            item = response.get('Item', {})
            messages = item.get('messages', [])
            for msg in messages:
                print(f"{msg['role']}: {msg['content']} ({msg['timestamp']})")
            return messages
        except ClientError as e:
            print(f"Erro ao consultar conversa: {e}")
            raise
