import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connected!")  # Отладочный вывод
        await self.channel_layer.group_add("chat_room", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected! Code: {close_code}")  # Отладочный вывод
        await self.channel_layer.group_discard("chat_room", self.channel_name)

    async def receive(self, text_data):
        print(f"Received message: {text_data}")  # Отладочный вывод
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']

            # Сохраняем сообщение
            await self.save_message(username, message)

            # Отправляем сообщение в группу
            await self.channel_layer.group_send(
                "chat_room",
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")  # Отладочный вывод

    async def chat_message(self, event):
        try:
            message = event['message']
            username = event['username']

            # Отправляем сообщение в WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'username': username
            }))
        except Exception as e:
            print(f"Error in chat_message: {e}")  # Отладочный вывод

    @database_sync_to_async
    def save_message(self, username, message):
        try:
            Message.objects.create(username=username, content=message)
        except Exception as e:
            print(f"Error saving message: {e}")  # Отладочный вывод 