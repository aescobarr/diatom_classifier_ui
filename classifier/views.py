from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from classifier.models import ClassificationModel, SingleRun
from classifier.classifier import create_temp_dir, unzip_to_dir, classify, create_results_dir, create_results_zip, create_summary
import os
from pathlib import Path
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse
import json

from django.shortcuts import get_object_or_404


def index(request):
    template = loader.get_template("classifier/index.html")
    models = ClassificationModel.objects.all()
    runs = SingleRun.objects.order_by('-run_at')
    context = {"models": models, "runs": runs}
    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template("classifier/about.html")
    return HttpResponse(template.render({}, request))


def classify_endpoint(request):
    if request.method == 'POST':

        params = json.loads(request.body)

        classification_model = get_object_or_404(ClassificationModel,pk=int( params['class_id'] ))
        classes = classification_model.get_classes_list()

        temp_dir = create_temp_dir()
        path_temp_dir = Path(temp_dir.name)
        dest_dir = os.path.join(path_temp_dir, "exploded")
        results_dir = os.path.join(path_temp_dir, "results")
        unzip_to_dir(params["file_path"], dest_dir)

        classification_result = classify(weights_file=classification_model.weights.path,pictures_dir=dest_dir,classes=classes)
        summary = create_summary(classification_result)

        create_results_dir(results_dir_root=results_dir, classification_result=classification_result, classes=classes)

        output_filename = create_results_zip(results_dir_root=results_dir)

        s = SingleRun(
            classification_model = classification_model,
            data_file = params["file_url"],
            results_summary = summary,
            results_file = str(os.path.join('media', 'outputs', output_filename + ".zip"))
        )
        s.save()

        return JsonResponse( {"success":True, "classification_result": classification_result} )


def file_uploader(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = default_storage.save(os.path.join("to_be_classified",uploaded_file.name), uploaded_file)  # Saves file
        file_url = default_storage.url(file_name)  # Public URL (if using media storage)

        # Extract filename with extension
        filename_with_ext = os.path.basename(file_name)

        # Absolute file path
        file_absolute_path = os.path.join(settings.MEDIA_ROOT, file_name)

        return JsonResponse({
            'success': True,
            'file_url': file_url,
            'filename': filename_with_ext,
            'file_path': file_absolute_path
        })

    return JsonResponse({'success': False, 'error': 'No file uploaded'})