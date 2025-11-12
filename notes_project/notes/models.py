from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='owned_notes', on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='collab_notes', blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=0)

    def create_version(self, editor):
        return NoteVersion.objects.create(
            note=self,
            title=self.title,
            content=self.content,
            editor=editor,
            version=self.version
        )

    def __str__(self):
        return self.title

class NoteVersion(models.Model):
    note = models.ForeignKey(Note, related_name='versions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()

    class Meta:
        ordering = ['-version']

