from django.db import models
from Instructors.models import Courses, Trivia, Instructors

# Create your models here.
class TriviaSession(models.Model):
    trivia_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, default=0)
    trivia_name = models.CharField(max_length=100)
    host = models.ForeignKey(Instructors, on_delete=models.CASCADE, default=0)
    trivia_reference = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.trivia_name
    
    def serialize(self):
        return {
            'trivia_id': self.trivia_id,
            'trivia_name': self.trivia_name,
            'trivia_reference': self.trivia_reference
        }
        