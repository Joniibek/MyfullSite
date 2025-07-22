import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import jwt



class MainConsumer(AsyncWebsocketConsumer):
        async def connect(self):                
                self.group_name = None
                token = self.scope["url_route"]["kwargs"]["token"]
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                self.user_id = decoded_token.get('user_id')
                self.group_name = f'user_{self.user_id}'
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.accept()

        async def disconnect(self, close_code):
                self.channel_layer.group_discard(self.group_name, self.channel_name)
                await self.close()  

        async def send_message(self, event):
                message = event['message']
                await self.send(text_data=message)



