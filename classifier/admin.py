from django.contrib import admin
from classifier.models import ClassificationModel, SingleRun

# Register your models here.
admin.site.register(ClassificationModel)
admin.site.register(SingleRun)