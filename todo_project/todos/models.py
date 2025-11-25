from django.db import models


class Todo(models.Model):
    """Basic TODO item the app manages."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_resolved", "due_date", "title"]

    def __str__(self) -> str:
        return self.title
