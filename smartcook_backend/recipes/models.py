from django.db import models

class Recipe(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    ingredients = models.JSONField()  # 리스트 그대로 저장
    steps = models.JSONField()        # 리스트 그대로 저장

    def __str__(self):
        return self.title
