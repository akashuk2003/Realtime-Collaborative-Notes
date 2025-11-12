import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Note
from .redis_utils import set_typing, get_typing_users, acquire_lock, release_lock
from asgiref.sync import sync_to_async

class NoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.note_id = self.scope['url_route']['kwargs']['note_id']
        self.group_name = f"note_{self.note_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        action = payload.get('action')
        user = self.scope["user"]
        if action == 'typing':
            await sync_to_async(set_typing)(self.note_id, user.id)
            typing = await sync_to_async(get_typing_users)(self.note_id)
            await self.channel_layer.group_send(self.group_name, {
                "type": "typing.update",
                "users": typing,
            })

        elif action == 'acquire_lock':
            key = f"note:{self.note_id}:lock"
            got = await sync_to_async(acquire_lock)(key, ttl=10)
            await self.channel_layer.group_send(self.group_name, {
                "type": "lock.update",
                "locked": got,
                "user": user.username
            })

        elif action == 'release_lock':
            key = f"note:{self.note_id}:lock"
            await sync_to_async(release_lock)(key)
            await self.channel_layer.group_send(self.group_name, {
                "type": "lock.update",
                "locked": False,
                "user": user.username
            })
            
    async def note_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "note_update",
            "note_id": event['note_id'],
            "title": event['title'],
            "content": event['content'],
            "version": event['version'],
        }))

    async def typing_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "users": event['users']
        }))

    async def lock_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "lock",
            "locked": event['locked'],
            "user": event.get('user')
        }))
