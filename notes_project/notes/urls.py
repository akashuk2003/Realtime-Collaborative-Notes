from django.urls import path
from .views import NoteListCreateView,NoteDetailView,NoteUpdateView,NoteVersionListView


urlpatterns=[
    path('notes/',NoteListCreateView.as_view(),name='note-list-create'),
    path('notes/<int:pk>/',NoteDetailView.as_view(),name='note-detail'),
    path('notes/<int:pk>/edit/',NoteUpdateView.as_view(),name='note-update'), 
    path('notes/<int:pk>/versions/',NoteVersionListView.as_view(),name='note-version-list'),
]