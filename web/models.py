from django.db import models

class User(models.Model):
    session_id = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    route = models.JSONField(null=True)
    stops = models.JSONField(null=True)
    distance = models.FloatField(null=True)

class Chat(models.Model):
    TYPE = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE)