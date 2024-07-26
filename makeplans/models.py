from django.db import models

class Student(models.Model):
    record_date = models.DateField()
    student_name = models.CharField(max_length=30)
    content = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.student_name}_{self.record_date}"