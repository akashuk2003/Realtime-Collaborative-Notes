from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.cache import cache
import json

class NoteVersionPagination(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        note_id = view.kwargs.get('pk') or request.query_params.get('note')
        page_number = request.query_params.get(self.page_query_param, 1)
        cache_key = f"note:{note_id}:versions:page:{page_number}"
        cached = cache.get(cache_key)
        if cached:
            self._cached_response = cached
            return []  
        qs = super().paginate_queryset(queryset, request, view)
        return qs

    def get_cached_response(self):
        return getattr(self, '_cached_response', None)
