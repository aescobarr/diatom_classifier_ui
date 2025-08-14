from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("ajax-upload/", views.file_uploader, name='ajax_upload'),
    path("ajax-classify/", views.classify_endpoint, name='ajax_classify'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)