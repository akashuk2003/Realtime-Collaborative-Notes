from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Note, NoteVersion
from .serializers import NoteSerializer, NoteUpdateSerializer, NoteVersionSerializer
from .pagination import NoteVersionPagination
from django.core.cache import cache

#View for Creating and Listing Notes
class NoteListCreateView(generics.ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        note = serializer.save(owner=self.request.user)
        note.version = 1
        note.save(update_fields=['version'])
        note.create_version(editor=self.request.user)
        note.collaborators.add(self.request.user)
        
#View for Specific Note Detail    
class NoteDetailView(generics.RetrieveAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
#Note Update View
class NoteUpdateView(generics.UpdateAPIView):
    queryset = Note.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return NoteUpdateSerializer
    
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        note = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        last_known = serializer.validated_data['last_known_version']
        if last_known != note.version:
            return Response(
                {"detail": "Conflict: note version mismatch."},
                status=status.HTTP_409_CONFLICT
            )

        note.title = serializer.validated_data.get('title', note.title)
        note.content = serializer.validated_data.get('content', note.content)
        note.version += 1
        note.save()
        note.create_version(editor=request.user)
        cache.delete_pattern(f"note:{note.id}:versions:*")
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"note_{note.id}", {
                "type": "note.update",
                "note_id": note.id,
                "title": note.title,
                "content": note.content,
                "version": note.version,
            }
        )
        return Response(NoteSerializer(note).data)
    

#NoteVersionList
class NoteVersionListView(generics.ListAPIView):
    serializer_class = NoteVersionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = NoteVersionPagination

    def get_queryset(self):
        note_id = self.kwargs['pk']
        return NoteVersion.objects.filter(note_id=note_id).order_by('-version')

    def list(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        paginator.page_size = self.pagination_class.page_size
        paginator.page_query_param = 'page'
        paginated = paginator.paginate_queryset(self.get_queryset(), request, self)
        cached = paginator.get_cached_response()
        if cached:
            return Response(cached)
        serializer = self.get_serializer(paginated, many=True)
        response = paginator.get_paginated_response(serializer.data)
        note_id = self.kwargs['pk']
        page_number = request.query_params.get('page', 1)
        cache_key = f"note:{note_id}:versions:page:{page_number}"
        cache.set(cache_key, response.data, timeout=30)
        return response
    
    
#View for Note Versions   
class NoteVersionListView(generics.ListAPIView):
    serializer_class = NoteVersionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = NoteVersionPagination

    def get_queryset(self):
        note_id = self.kwargs['pk']
        return NoteVersion.objects.filter(note_id=note_id).order_by('-version')

    def list(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        paginator.page_size = self.pagination_class.page_size
        paginator.page_query_param = 'page'
        paginated = paginator.paginate_queryset(self.get_queryset(), request, self)
        cached = paginator.get_cached_response()
        if cached:
            return Response(cached)
        serializer = self.get_serializer(paginated, many=True)
        response = paginator.get_paginated_response(serializer.data)
        note_id = self.kwargs['pk']
        page_number = request.query_params.get('page', 1)
        cache_key = f"note:{note_id}:versions:page:{page_number}"
        cache.set(cache_key, response.data, timeout=30) 
        return response


