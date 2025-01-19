from channels.generic.websocket import AsyncWebsocketConsumer
import json


class SyncTokenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "table_updates"

        # Adiciona o WebSocket ao grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove o WebSocket do grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "Evento desconhecido.")

        # Envia mensagem para o grupo
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "table_update",
                "message": message,
            },
        )

    async def table_update(self, event):
        # Envia a mensagem de volta ao WebSocket
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
