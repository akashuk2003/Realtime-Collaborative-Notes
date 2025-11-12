from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notes/<int:note_id>/', consumers.NoteConsumer.as_asgi()),
]
