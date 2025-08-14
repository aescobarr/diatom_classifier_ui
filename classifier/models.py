from django.db import models
import os
# Create your models here.

PLATFORM_CHOICES = [
    ("cpu", "CPU"),
    ("gpu", "GPU"),
]


class ClassificationModel(models.Model):
    description = models.TextField()
    weights = models.FileField(upload_to='models/')
    classes = models.TextField()
    runs_on = models.CharField(max_length=3, choices=PLATFORM_CHOICES, default="cpu")

    def __str__(self):
        return os.path.basename(self.weights.path)

    def get_classes_list(self):
        class_list = [ f.strip() for f in self.classes.split(",") ]
        return class_list


class SingleRun(models.Model):
    run_at = models.DateTimeField(auto_now_add=True)
    classification_model = models.ForeignKey(ClassificationModel, on_delete=models.CASCADE, related_name="runs")
    data_file = models.CharField(max_length=512)
    results_file = models.CharField(max_length=512, blank=True)
    results_summary = models.CharField(max_length=512)